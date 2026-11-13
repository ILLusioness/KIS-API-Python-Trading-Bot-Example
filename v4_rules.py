# V4.0 order sizing and turn updates.
# Holdings stay in the ledger. T is a running state, not cost divided by a fixed portion.

def official_target_percent(ticker, configured):
    key = str(ticker or "").strip().upper()
    if key == "TQQQ":
        return 15.0
    if key == "SOXL":
        return 20.0
    try:
        return float(configured)
    except (TypeError, ValueError):
        return 0.0


def legacy_progress_t(holdings, avg_price, seed, split):
    """One-time bridge so an existing position keeps its depth on the first V4 boot."""
    holdings = float(holdings or 0.0)
    avg_price = float(avg_price or 0.0)
    seed = float(seed or 0.0)
    split = float(split or 0.0)
    if holdings <= 0 or avg_price <= 0 or seed <= 0 or split <= 0:
        return 0.0
    portion = seed / split
    if portion <= 0:
        return 0.0
    return (holdings * avg_price) / portion


def one_buy_amount(remaining_cash, split, t_val):
    remaining_cash = max(0.0, float(remaining_cash or 0.0))
    split = float(split or 0.0)
    t_val = float(t_val or 0.0)
    if split <= 0:
        return remaining_cash
    slots = split - t_val
    if slots <= 0:
        return remaining_cash
    return remaining_cash / slots


def reverse_sell_divisor(split):
    split = float(split or 0.0)
    if split <= 0:
        return 10
    return max(1, int(split // 2))


def apply_normal_day(t_val, one_portion, prior_qty, buy_amount, sell_qty):
    """Apply one session of normal-mode fills.

    Sells are applied before buys, so a target-limit sale followed by an LOC buy
    becomes T * 0.25 + 1 (or + 0.5). A flat close with no new buy resets T to 0.
    """
    t_val = float(t_val or 0.0)
    one_portion = max(0.0, float(one_portion or 0.0))
    prior_qty = int(prior_qty or 0)
    buy_amount = max(0.0, float(buy_amount or 0.0))
    sell_qty = int(sell_qty or 0)

    if prior_qty > 0 and sell_qty > 0:
        ratio = sell_qty / float(prior_qty)
        if ratio >= 0.90:
            t_val = 0.0
        elif ratio >= 0.50:
            t_val *= 0.25
        elif ratio >= 0.15:
            t_val *= 0.75

    if one_portion > 0 and buy_amount >= one_portion * 0.75:
        t_val += 1.0
    elif one_portion > 0 and buy_amount >= one_portion * 0.35:
        t_val += 0.5

    if t_val < 0:
        return 0.0
    return t_val


def apply_reverse_day(t_val, split, had_sell, had_buy):
    t_val = float(t_val or 0.0)
    split = float(split or 0.0)
    if split <= 0:
        return t_val
    if had_sell:
        t_val *= (1.0 - (2.0 / split))
    if had_buy:
        t_val += (split - t_val) * 0.25
    if t_val < 0:
        return 0.0
    return t_val
