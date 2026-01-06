"""
Epic 3: E2E Feature Verification Tests for v1.3
Tests hybrid, solo, and NLQ modes end-to-end
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit
class MockStreamlit:
    session_state = {}
    def set_page_config(**kwargs): pass
    def markdown(text, **kwargs): pass
    def write(text): pass

sys.modules['streamlit'] = MockStreamlit()

from app import (
    parse_nlq_intent, generate_mock_df, generate_nlq_insights,
    generate_nlq_stories, calculate_nlq_score, detect_echo_chambers,
    analyze_sentiment_basic, calculate_mismatch_score, extract_keywords,
    validate_text_input, validate_csv_input, validate_query_input,
    health_check
)

class TestE2EHybridMode(unittest.TestCase):
    """Test hybrid mode: TXT + CSV analysis"""
    
    def setUp(self):
        """Setup test data"""
        self.meeting_notes = """
        Team Meeting - Q4 Strategy
        Urban market is booming. Urban customers love our premium line.
        Urban growth is 15% this quarter. Urban is the future.
        We should focus on urban expansion. Urban, urban, urban.
        """
        
        self.sales_data = pd.DataFrame({
            'Date': pd.date_range('2025-10-01', periods=10),
            'Region': ['Urban', 'Rural', 'Suburban'] * 3 + ['Urban'],
            'Revenue': [7000, 5000, 6000, 7100, 4900, 6100, 7200, 5100, 6200, 7300],
            'Units_Sold': [140, 80, 110, 142, 78, 112, 144, 82, 114, 146]
        })
    
    def test_hybrid_echo_detection(self):
        """Test echo chamber detection in meeting notes"""
        echoes = detect_echo_chambers(self.meeting_notes)
        
        self.assertGreater(len(echoes), 0)
        self.assertEqual(echoes[0]['keyword'], 'urban')
        self.assertGreaterEqual(echoes[0]['frequency'], 5)
        print("✅ Hybrid: Echo detection works")
    
    def test_hybrid_mismatch_score(self):
        """Test mismatch between text and data"""
        mismatch = calculate_mismatch_score(self.meeting_notes, self.sales_data)
        
        # Should detect mismatch: team focused on urban, but rural growing
        self.assertGreater(mismatch, 40)
        print("✅ Hybrid: Mismatch detection works")
    
    def test_hybrid_sentiment(self):
        """Test sentiment analysis"""
        sentiment = analyze_sentiment_basic(self.meeting_notes)
        
        self.assertGreater(sentiment, 50)  # Positive tone
        print("✅ Hybrid: Sentiment analysis works")
    
    def test_hybrid_e2e(self):
        """End-to-end hybrid flow"""
        # 1. Detect echoes
        echoes = detect_echo_chambers(self.meeting_notes)
        self.assertGreater(len(echoes), 0)
        
        # 2. Calculate mismatch
        mismatch = calculate_mismatch_score(self.meeting_notes, self.sales_data)
        self.assertGreater(mismatch, 0)
        
        # 3. Get sentiment
        sentiment = analyze_sentiment_basic(self.meeting_notes)
        self.assertGreater(sentiment, 0)
        
        print("✅ Hybrid E2E: Complete flow works (echo + mismatch + sentiment)")

class TestE2ESoloMode(unittest.TestCase):
    """Test solo mode: CSV analysis only"""
    
    def setUp(self):
        """Setup test data"""
        self.dirty_csv = pd.DataFrame({
            'Date': pd.date_range('2025-10-01', periods=10),
            'Region': ['Urban', 'Rural', 'Suburban', None, 'Urban', 'Rural', 'Suburban', 'Urban', 'Rural', 'Suburban'],
            'Revenue': [7000, 5000, 6000, np.nan, 7100, 4900, 6100, 7200, 5100, 6200],
            'Units_Sold': [140, 80, 110, 100, 142, 78, 112, 144, 82, 114]
        })
    
    def test_solo_csv_validation(self):
        """Test CSV validation"""
        validated = validate_csv_input(self.dirty_csv)
        
        self.assertIsNotNone(validated)
        self.assertEqual(len(validated), 10)
        print("✅ Solo: CSV validation works")
    
    def test_solo_data_analysis(self):
        """Test data analysis on CSV"""
        df = self.dirty_csv.dropna()
        
        # Calculate regional stats
        regional_stats = df.groupby('Region')['Revenue'].agg(['mean', 'sum', 'count'])
        
        self.assertGreater(len(regional_stats), 0)
        self.assertIn('Urban', regional_stats.index)
        print("✅ Solo: Data analysis works")
    
    def test_solo_e2e(self):
        """End-to-end solo flow"""
        # 1. Validate CSV
        validated = validate_csv_input(self.dirty_csv)
        self.assertIsNotNone(validated)
        
        # 2. Clean data
        clean_df = validated.dropna()
        self.assertGreater(len(clean_df), 0)
        
        # 3. Generate insights
        regional_stats = clean_df.groupby('Region')['Revenue'].mean()
        self.assertGreater(len(regional_stats), 0)
        
        print("✅ Solo E2E: Complete flow works (validate + clean + analyze)")

class TestE2ENLQMode(unittest.TestCase):
    """Test NLQ mode: Natural language query processing"""
    
    def test_nlq_query_validation(self):
        """Test query validation"""
        valid_query = validate_query_input("Sales dropping in rural areas")
        self.assertIsNotNone(valid_query)
        
        invalid_query = validate_query_input("")
        self.assertIsNone(invalid_query)
        
        print("✅ NLQ: Query validation works")
    
    def test_nlq_intent_parsing(self):
        """Test intent parsing"""
        queries = [
            ("Sales dropping in rural areas", "sales_issue"),
            ("What growth can I expect?", "forecast"),
            ("Team focused on premium but budget growing", "bias_check"),
        ]
        
        for query, expected_intent in queries:
            result = parse_nlq_intent(query)
            self.assertEqual(result['intent'], expected_intent)
        
        print("✅ NLQ: Intent parsing works")
    
    def test_nlq_story_generation(self):
        """Test story generation"""
        query_data = parse_nlq_intent("Sales dropping in rural areas")
        df = generate_mock_df(query_data)
        insights = generate_nlq_insights(query_data, df)
        stories = generate_nlq_stories(query_data, df, insights)
        
        self.assertGreater(len(stories), 0)
        self.assertGreater(len(stories), 2)  # At least 3 paths
        
        for story in stories:
            self.assertIn('title', story)
            self.assertIn('growth', story)
            self.assertIn('risk', story)
        
        print("✅ NLQ: Story generation works")
    
    def test_nlq_score_calculation(self):
        """Test score calculation"""
        query_data = parse_nlq_intent("Sales dropping")
        df = generate_mock_df(query_data)
        insights = generate_nlq_insights(query_data, df)
        score = calculate_nlq_score(query_data, insights)
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        print("✅ NLQ: Score calculation works")
    
    def test_nlq_e2e(self):
        """End-to-end NLQ flow"""
        # 1. Validate query
        query = validate_query_input("Village sales low—fix?")
        self.assertIsNotNone(query)
        
        # 2. Parse intent
        query_data = parse_nlq_intent(query)
        self.assertIsNotNone(query_data['intent'])
        
        # 3. Generate mock data
        df = generate_mock_df(query_data)
        self.assertGreater(len(df), 0)
        
        # 4. Generate insights
        insights = generate_nlq_insights(query_data, df)
        self.assertGreater(len(insights), 0)
        
        # 5. Generate stories
        stories = generate_nlq_stories(query_data, df, insights)
        self.assertGreater(len(stories), 0)
        
        # 6. Calculate score
        score = calculate_nlq_score(query_data, insights)
        self.assertGreater(score, 0)
        
        print("✅ NLQ E2E: Complete flow works (query → intent → data → insights → stories → score)")

class TestHealthCheck(unittest.TestCase):
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health check returns status"""
        result = health_check()
        
        self.assertIn('status', result)
        self.assertEqual(result['status'], "Nexus Alive!")
        self.assertIn('timestamp', result)
        print("✅ Health: Health check works")

def run_e2e_tests():
    """Run all E2E tests"""
    print("=" * 70)
    print("🧪 EPIC 3: E2E FEATURE VERIFICATION TESTS")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestE2EHybridMode))
    suite.addTests(loader.loadTestsFromTestCase(TestE2ESoloMode))
    suite.addTests(loader.loadTestsFromTestCase(TestE2ENLQMode))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthCheck))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ ALL E2E TESTS PASSED!")
        print(f"Tests run: {result.testsRun}")
        print("Status: Ready for production deployment")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_e2e_tests()
    sys.exit(0 if success else 1)
