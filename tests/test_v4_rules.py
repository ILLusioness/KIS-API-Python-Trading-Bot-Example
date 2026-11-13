import unittest

from v4_rules import (
    apply_normal_day,
    apply_reverse_day,
    legacy_progress_t,
    official_target_percent,
    one_buy_amount,
    reverse_sell_divisor,
)


class V4RulesTest(unittest.TestCase):
    def test_official_targets(self):
        self.assertEqual(official_target_percent("TQQQ", 10), 15.0)
        self.assertEqual(official_target_percent("soxl", 12), 20.0)
        self.assertEqual(official_target_percent("QQQ", 8), 8.0)

    def test_existing_position_keeps_depth(self):
        # 10 shares at $50, seed 20000, 40 splits → cost equals 10 portions.
        self.assertAlmostEqual(legacy_progress_t(10, 50, 20000, 40), 1.0)

    def test_one_buy_uses_remaining_slots(self):
        self.assertAlmostEqual(one_buy_amount(19522, 40, 1), 19522 / 39)

    def test_quarter_sell_then_full_buy(self):
        t = apply_normal_day(10, 500, prior_qty=100, buy_amount=500, sell_qty=25)
        self.assertAlmostEqual(t, 10 * 0.75 + 1)

    def test_target_sell_then_half_buy(self):
        t = apply_normal_day(8, 400, prior_qty=80, buy_amount=200, sell_qty=60)
        self.assertAlmostEqual(t, 8 * 0.25 + 0.5)

    def test_flat_close_resets_turn(self):
        self.assertEqual(apply_normal_day(12, 500, 40, 0, 40), 0.0)

    def test_unfilled_day_does_not_move_turn(self):
        self.assertEqual(apply_normal_day(4, 500, 20, 0, 0), 4)

    def test_reverse_40_split(self):
        after_sell = apply_reverse_day(39.5, 40, had_sell=True, had_buy=False)
        self.assertAlmostEqual(after_sell, 39.5 * 0.95)
        after_buy = apply_reverse_day(after_sell, 40, had_sell=False, had_buy=True)
        self.assertAlmostEqual(after_buy, after_sell + (40 - after_sell) * 0.25)

    def test_reverse_sell_divisor(self):
        self.assertEqual(reverse_sell_divisor(20), 10)
        self.assertEqual(reverse_sell_divisor(30), 15)
        self.assertEqual(reverse_sell_divisor(40), 20)


if __name__ == "__main__":
    unittest.main()
