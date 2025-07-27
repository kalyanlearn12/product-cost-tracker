
import unittest
from unittest.mock import patch
from product_tracker.tracker import track_product, schedule_product_tracking, scheduled_products, save_scheduled, load_scheduled, delete_scheduled

class TestProductCostTracker(unittest.TestCase):
    def test_chatid_picklist_and_custom(self):
        # Simulate backend logic for picklist and custom chatid
        def resolve_chatid(chatid_pick, custom_chatid):
            if chatid_pick == 'custom':
                return custom_chatid or '249722033'
            else:
                return chatid_pick or '249722033'
        # Picklist kalyan
        self.assertEqual(resolve_chatid('249722033', ''), '249722033')
        # Picklist uma
        self.assertEqual(resolve_chatid('258922383', ''), '258922383')
        # Custom chatid
        self.assertEqual(resolve_chatid('custom', '999999999'), '999999999')
        # Custom chatid blank falls back to kalyan
        self.assertEqual(resolve_chatid('custom', ''), '249722033')

    @patch('product_tracker.tracker.scrape_price')
    @patch('product_tracker.tracker.send_telegram_message')
    def test_telegram_notification_sent(self, mock_send_telegram, mock_scrape):
        mock_scrape.return_value = (49999, 'Test Product')
        result = track_product(
            product_url='https://www.myntra.com/test-product',
            target_price=50000,
            notify_method='telegram',
            phone_or_chat='249722033',
            check_alternates=False
        )
        self.assertIn('Notification sent', result)
        mock_send_telegram.assert_called_once()


    @patch('product_tracker.tracker.scrape_price')
    @patch('product_tracker.tracker.send_telegram_message')
    def test_no_notification_above_target(self, mock_send_telegram, mock_scrape):
        mock_scrape.return_value = (51000, 'Test Product')
        result = track_product(
            product_url='https://www.myntra.com/test-product',
            target_price=50000,
            notify_method='telegram',
            phone_or_chat='249722033',
            check_alternates=False
        )
        self.assertIn('No deal found', result)
        mock_send_telegram.assert_not_called()

    def test_schedule_and_persistence(self):
        # Clear and test scheduling and persistence
        scheduled_products.clear()
        schedule_product_tracking('http://example.com', 100, None, '111', False, 2)
        save_scheduled()
        loaded = load_scheduled()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]['product_url'], 'http://example.com')
        delete_scheduled(0)
        save_scheduled()
        loaded2 = load_scheduled()
        self.assertEqual(len(loaded2), 0)

    def test_default_chat_id(self):
        # Should use default chat id if blank
        with patch('product_tracker.tracker.send_telegram_message') as mock_send:
            with patch('product_tracker.tracker.scrape_price') as mock_scrape:
                mock_scrape.return_value = (100, 'Test')
                result = track_product('url', 200, 'telegram', '', False)
                self.assertIn('Notification sent', result)

if __name__ == '__main__':
    unittest.main()
