from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml


OUTPUT_FIELDS = [
    "value",
    "board_value",
    "body_value",
    "hand_plus",
    "opponent_hand_plus",
    "threat_power",
    "threat_value",
    "survival_power",
    "survival_value",
    "convert_power",
    "convert_value",
]


@dataclass(frozen=True)
class Card:
    id: str
    name: str
    type: str
    lv: int
    cost: int
    ap: int
    hp: int
    resonance_kind: str | None
    resonance_values: tuple[str, ...]


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as file:
        return yaml.safe_load(file)


def parse_int(value) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def parse_decklist(path: Path) -> list[tuple[str, int]]:
    entries: list[tuple[str, int]] = []
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        count_text, card_id = line.split("x", 1)
        entries.append((card_id.strip(), int(count_text.strip())))
    return entries


def load_cards(path: Path) -> dict[str, Card]:
    data = load_yaml(path)
    cards: dict[str, Card] = {}
    for row in data["cards"]:
        resonance = row.get("resonance") or {}
        cards[row["id"]] = Card(
            id=row["id"],
            name=row["name"],
            type=row["type"],
            lv=parse_int(row["lv"]),
            cost=parse_int(row["cost"]),
            ap=parse_int(row.get("ap")),
            hp=parse_int(row.get("hp")),
            resonance_kind=resonance.get("kind"),
            resonance_values=tuple(resonance.get("values") or []),
        )
    return cards


def load_value_table(path: Path) -> dict[str, dict]:
    data = load_yaml(path)
    return {row["name"]: row for row in data["effects"]}


def zero_outputs() -> dict[str, float]:
    return {field: 0.0 for field in OUTPUT_FIELDS}


def add_outputs(base: dict[str, float], extra: dict[str, float], scale: float = 1.0) -> dict[str, float]:
    result = dict(base)
    for field in OUTPUT_FIELDS:
        value = extra.get(field, 0)
        if isinstance(value, (int, float)):
            result[field] += value * scale
    return result


def effect_outputs(effect_row: dict, scale: float = 1.0) -> dict[str, float]:
    outputs = zero_outputs()
    raw_outputs = effect_row.get("outputs", {})
    for field in OUTPUT_FIELDS:
        value = raw_outputs.get(field)
        if isinstance(value, (int, float)):
            outputs[field] = value * scale
    return outputs


def body_total(card: Card) -> int:
    return card.ap + card.hp


def scenario_resource(turn: int) -> tuple[int, int]:
    return turn + 1, turn


def build_card_models(cards: dict[str, Card], value_table: dict[str, dict]) -> dict[str, list[dict]]:
    models: dict[str, list[dict]] = {}
    machine_default = value_table.get("所有机器默认", {"outputs": {}})
    body_effect = value_table.get("身材", {"outputs": {}})
    resonance_effect = value_table.get("共鸣", {"outputs": {}})

    for card in cards.values():
        rows: list[dict] = []
        if card.type == "机体":
            rows.append(
                {
                    "kind": "unconditional",
                    "label": "所有机器默认",
                    "outputs": effect_outputs(machine_default),
                }
            )
            rows.append(
                {
                    "kind": "unconditional",
                    "label": "身材",
                    "outputs": effect_outputs(body_effect, scale=body_total(card)),
                }
            )
            if card.resonance_values:
                rows.append(
                    {
                        "kind": "conditional",
                        "condition_class": "resonance",
                        "condition_param": list(card.resonance_values),
                        "label": "共鸣",
                        "outputs": effect_outputs(resonance_effect),
                    }
                )
        models[card.id] = rows
    return models


def init_draw_distribution(deck_counts: list[int], draw_n: int):
    states = {(tuple([0] * len(deck_counts)), tuple(deck_counts)): 1.0}
    for _ in range(draw_n):
        next_states = defaultdict(float)
        for (hand, deck), prob in states.items():
            total = sum(deck)
            if total == 0:
                continue
            for idx, count in enumerate(deck):
                if count <= 0:
                    continue
                next_hand = list(hand)
                next_deck = list(deck)
                next_hand[idx] += 1
                next_deck[idx] -= 1
                next_states[(tuple(next_hand), tuple(next_deck))] += prob * count / total
        states = next_states
    return states


def resonance_probability(
    card: Card,
    hand: tuple[int, ...],
    played: tuple[int, ...],
    ids: tuple[str, ...],
    rem_cost: int,
    lv: int,
    cards: dict[str, Card],
) -> float:
    if not card.resonance_values:
        return 0.0

    wanted = set(card.resonance_values)

    for idx, count in enumerate(played):
        if count > 0 and cards[ids[idx]].name in wanted:
            return 1.0

    rem_after = rem_cost - card.cost
    if rem_after < 0:
        return 0.0

    for idx, count in enumerate(hand):
        if count <= 0:
            continue
        other = cards[ids[idx]]
        if other.type != "机师":
            continue
        if other.name in wanted and other.lv <= lv and other.cost <= rem_after:
            return 1.0

    return 0.0


def evaluate_card(
    card: Card,
    model_rows: list[dict],
    hand: tuple[int, ...],
    played: tuple[int, ...],
    ids: tuple[str, ...],
    rem_cost: int,
    lv: int,
    cards: dict[str, Card],
    fallback_prob: float,
) -> dict[str, float]:
    total = zero_outputs()
    for row in model_rows:
        if row["kind"] == "unconditional":
            total = add_outputs(total, row["outputs"])
        elif row["kind"] == "conditional":
            if row.get("condition_class") == "resonance":
                prob = resonance_probability(card, hand, played, ids, rem_cost, lv, cards)
            else:
                prob = fallback_prob
            total = add_outputs(total, row["outputs"], prob)
    return total


def hand_text(hand: tuple[int, ...], ids: tuple[str, ...]) -> str:
    parts = [f"{ids[idx]}x{count}" for idx, count in enumerate(hand) if count]
    return " / ".join(parts) if parts else "empty"


def compress_actions(actions: list[str]) -> str:
    if not actions:
        return "pass"
    out: list[str] = []
    current = actions[0]
    count = 1
    for action in actions[1:]:
        if action == current:
            count += 1
        else:
            out.append(f"{current}x{count}")
            current = action
            count = 1
    out.append(f"{current}x{count}")
    return " -> ".join(out)


def run_simulation(
    cards: dict[str, Card],
    value_table: dict[str, dict],
    deck_entries: list[tuple[str, int]],
    turns: int,
    fallback_prob: float,
):
    ids = tuple(card_id for card_id, _ in deck_entries)
    deck_counts = [count for _, count in deck_entries]
    models = build_card_models(cards, value_table)
    states = init_draw_distribution(deck_counts, 6)
    summaries: list[dict] = []
    details: list[dict] = []

    @lru_cache(maxsize=None)
    def greedy(hand: tuple[int, ...], lv: int, cost: int):
        hand_list = list(hand)
        rem_cost = cost
        played = [0] * len(hand)
        actions: list[str] = []
        outputs = zero_outputs()

        while True:
            best_score = None
            best_idx = None
            best_outputs = None

            for idx, count in enumerate(hand_list):
                if count <= 0:
                    continue

                card = cards[ids[idx]]
                if card.lv > lv or card.cost > rem_cost:
                    continue

                current = evaluate_card(
                    card=card,
                    model_rows=models.get(card.id, []),
                    hand=tuple(hand_list),
                    played=tuple(played),
                    ids=ids,
                    rem_cost=rem_cost,
                    lv=lv,
                    cards=cards,
                    fallback_prob=fallback_prob,
                )
                score = (
                    current["board_value"],
                    current["value"],
                    current["threat_power"] + current["threat_value"],
                    current["survival_power"] + current["survival_value"],
                    -card.cost,
                )
                if best_score is None or score > best_score:
                    best_score = score
                    best_idx = idx
                    best_outputs = current

            if best_score is None or best_score[0] <= 0:
                break

            hand_list[best_idx] -= 1
            played[best_idx] += 1
            rem_cost -= cards[ids[best_idx]].cost
            actions.append(ids[best_idx])
            outputs = add_outputs(outputs, best_outputs)

        return tuple(hand_list), outputs, actions, rem_cost

    for turn in range(1, turns + 1):
        lv, cost = scenario_resource(turn)
        aggregate = zero_outputs()
        action_prob = defaultdict(float)
        next_states = defaultdict(float)
        merged_details = defaultdict(
            lambda: {
                "prob": 0.0,
                "outputs": zero_outputs(),
                "actions": "pass",
                "rem_cost": cost,
            }
        )

        for (hand, deck), prob in states.items():
            hand_after, outputs, actions, rem_cost = greedy(hand, lv, cost)

            for field in OUTPUT_FIELDS:
                aggregate[field] += outputs[field] * prob

            action_text = compress_actions(actions)
            action_prob[action_text] += prob
            merged_details[hand]["prob"] += prob
            merged_details[hand]["outputs"] = outputs
            merged_details[hand]["actions"] = action_text
            merged_details[hand]["rem_cost"] = rem_cost

            if turn < turns:
                total = sum(deck)
                if total == 0:
                    next_states[(hand_after, deck)] += prob
                else:
                    for idx, count in enumerate(deck):
                        if count <= 0:
                            continue
                        next_hand = list(hand_after)
                        next_deck = list(deck)
                        next_hand[idx] += 1
                        next_deck[idx] -= 1
                        next_states[(tuple(next_hand), tuple(next_deck))] += prob * count / total

        common_action, common_prob = max(action_prob.items(), key=lambda item: item[1])
        summaries.append(
            {
                "turn": turn,
                "lv": lv,
                "cost": cost,
                "state_count": len(states),
                "expected": aggregate,
                "most_common_action": common_action,
                "most_common_action_prob": common_prob,
            }
        )

        for hand, data in sorted(merged_details.items(), key=lambda item: item[1]["prob"], reverse=True):
            details.append(
                {
                    "turn": turn,
                    "lv": lv,
                    "cost": cost,
                    "prob": data["prob"],
                    "hand": hand_text(hand, ids),
                    "actions": data["actions"],
                    "outputs": data["outputs"],
                    "rem_cost": data["rem_cost"],
                }
            )

        states = next_states

    return {
        "deck_ids": list(ids),
        "summaries": summaries,
        "details": details,
    }


def main():
    parser = argparse.ArgumentParser(description="Run a git-friendly P2-2 greedy simulation from text data.")
    parser.add_argument("--cards", default="data/cards/cards.yaml")
    parser.add_argument("--values", default="data/value_tables/value_table.yaml")
    parser.add_argument("--deck", default="data/decks/blue_purple_sample_50.txt")
    parser.add_argument("--scenario", default="data/scenarios/p22_blue_purple_sample.yaml")
    parser.add_argument("--output", default="output/p22_blue_purple_sample.json")
    parser.add_argument("--turns", type=int, default=None)
    args = parser.parse_args()

    cards = load_cards(Path(args.cards))
    value_table = load_value_table(Path(args.values))
    deck_entries = parse_decklist(Path(args.deck))
    scenario = load_yaml(Path(args.scenario))["scenario"]

    result = run_simulation(
        cards=cards,
        value_table=value_table,
        deck_entries=deck_entries,
        turns=int(args.turns or scenario["turns"]),
        fallback_prob=float(scenario["fallback_condition_probability"]),
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(output_path)


if __name__ == "__main__":
    main()
