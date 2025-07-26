
import unittest
from unittest.mock import patch
from product_tracker.tracker import track_product, schedule_product_tracking, scheduled_products, save_scheduled, load_scheduled, delete_scheduled

class TestProductCostTracker(unittest.TestCase):

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
