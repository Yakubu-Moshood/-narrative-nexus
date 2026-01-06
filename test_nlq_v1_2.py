"""
Test Suite for Narrative Nexus v1.2 - NLQ Mode
Tests NLQ parsing, mock data generation, insights, and story weaving
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Import app functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit for testing
class MockStreamlit:
    @staticmethod
    def set_page_config(**kwargs):
        pass
    
    @staticmethod
    def markdown(text, **kwargs):
        pass
    
    @staticmethod
    def write(text):
        pass

sys.modules['streamlit'] = MockStreamlit()

# Now we can import the functions we need to test
from app import (
    parse_nlq_intent,
    generate_mock_df,
    generate_nlq_insights,
    generate_nlq_stories,
    calculate_nlq_score,
    extract_keywords,
    detect_echo_chambers,
    analyze_sentiment_basic,
    calculate_mismatch_score,
    run_monte_carlo_simulation
)

class TestNLQMode(unittest.TestCase):
    """Test NLQ Mode functionality"""
    
    def test_parse_nlq_intent_sales_issue(self):
        """Test parsing sales issue intent"""
        query = "My cafe sales down 20%—how to boost?"
        result = parse_nlq_intent(query)
        
        self.assertEqual(result['intent'], 'sales_issue')
        self.assertIn('sentiment', result)
        self.assertIn('key_terms', result)
        print("✅ test_parse_nlq_intent_sales_issue passed")
    
    def test_parse_nlq_intent_forecast(self):
        """Test parsing forecast intent"""
        query = "What growth can I expect next quarter?"
        result = parse_nlq_intent(query)
        
        self.assertEqual(result['intent'], 'forecast')
        print("✅ test_parse_nlq_intent_forecast passed")
    
    def test_parse_nlq_intent_bias_check(self):
        """Test parsing bias check intent"""
        query = "Team focused on premium but budget growing faster—what's happening?"
        result = parse_nlq_intent(query)
        
        self.assertEqual(result['intent'], 'bias_check')
        print("✅ test_parse_nlq_intent_bias_check passed")
    
    def test_parse_nlq_sentiment_negative(self):
        """Test sentiment detection - negative"""
        query = "Sales dropped 30%, customers are unhappy, we have major problems"
        result = parse_nlq_intent(query)
        
        self.assertEqual(result['sentiment'], 'negative')
        print("✅ test_parse_nlq_sentiment_negative passed")
    
    def test_parse_nlq_sentiment_positive(self):
        """Test sentiment detection - positive"""
        query = "Revenue is growing great, amazing opportunity ahead"
        result = parse_nlq_intent(query)
        
        self.assertEqual(result['sentiment'], 'positive')
        print("✅ test_parse_nlq_sentiment_positive passed")
    
    def test_generate_mock_df_sales_issue(self):
        """Test mock data generation for sales issue"""
        query_data = {'intent': 'sales_issue', 'key_terms': [], 'sentiment': 'negative', 'query': ''}
        df = generate_mock_df(query_data)
        
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        self.assertIn('Revenue', df.columns)
        self.assertIn('Region', df.columns)
        
        # Check declining trend for sales issue
        self.assertGreater(df['Revenue'].iloc[0], df['Revenue'].iloc[-1])
        print("✅ test_generate_mock_df_sales_issue passed")
    
    def test_generate_mock_df_forecast(self):
        """Test mock data generation for forecast"""
        query_data = {'intent': 'forecast', 'key_terms': [], 'sentiment': 'positive', 'query': ''}
        df = generate_mock_df(query_data)
        
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        
        # Check growing trend for forecast
        self.assertLess(df['Revenue'].iloc[0], df['Revenue'].iloc[-1])
        print("✅ test_generate_mock_df_forecast passed")
    
    def test_generate_nlq_insights_sales_issue(self):
        """Test insights generation for sales issue"""
        query_data = {'intent': 'sales_issue', 'key_terms': [], 'sentiment': 'negative', 'query': ''}
        df = generate_mock_df(query_data)
        insights = generate_nlq_insights(query_data, df)
        
        self.assertGreater(len(insights), 0)
        self.assertGreater(len(insights), 2)
        
        # Check for specific keywords in insights
        insights_text = ' '.join(insights).lower()
        self.assertIn('revenue', insights_text)
        print("✅ test_generate_nlq_insights_sales_issue passed")
    
    def test_generate_nlq_insights_bias_check(self):
        """Test insights generation for bias check"""
        query_data = {'intent': 'bias_check', 'key_terms': [], 'sentiment': 'neutral', 'query': ''}
        df = generate_mock_df(query_data)
        insights = generate_nlq_insights(query_data, df)
        
        self.assertGreater(len(insights), 0)
        insights_text = ' '.join(insights).lower()
        self.assertIn('regional', insights_text)
        print("✅ test_generate_nlq_insights_bias_check passed")
    
    def test_generate_nlq_stories_sales_issue(self):
        """Test story generation for sales issue"""
        query_data = {'intent': 'sales_issue', 'key_terms': [], 'sentiment': 'negative', 'query': 'Sales down'}
        df = generate_mock_df(query_data)
        insights = generate_nlq_insights(query_data, df)
        stories = generate_nlq_stories(query_data, df, insights)
        
        self.assertEqual(len(stories), 4)
        
        # Check story structure
        for story in stories:
            self.assertIn('title', story)
            self.assertIn('description', story)
            self.assertIn('outcome', story)
            self.assertIn('growth', story)
            self.assertIn('risk', story)
        
        print("✅ test_generate_nlq_stories_sales_issue passed")
    
    def test_calculate_nlq_score(self):
        """Test Nexus Advice Score calculation"""
        query_data = {'intent': 'sales_issue', 'key_terms': [], 'sentiment': 'negative', 'query': ''}
        insights = ['Insight 1', 'Insight 2', 'Insight 3']
        score = calculate_nlq_score(query_data, insights)
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertGreater(score, 70)  # Should be reasonably high
        print("✅ test_calculate_nlq_score passed")
    
    def test_nlq_end_to_end_workflow(self):
        """Test complete NLQ workflow"""
        # User query
        query = "Sales dropping in rural areas—how can I fix it?"
        
        # Step 1: Parse intent
        query_data = parse_nlq_intent(query)
        self.assertEqual(query_data['intent'], 'sales_issue')
        
        # Step 2: Generate mock data
        df = generate_mock_df(query_data)
        self.assertIsNotNone(df)
        
        # Step 3: Generate insights
        insights = generate_nlq_insights(query_data, df)
        self.assertGreater(len(insights), 0)
        
        # Step 4: Generate stories
        stories = generate_nlq_stories(query_data, df, insights)
        self.assertEqual(len(stories), 4)
        
        # Step 5: Calculate score
        score = calculate_nlq_score(query_data, insights)
        self.assertGreater(score, 0)
        
        print("✅ test_nlq_end_to_end_workflow passed")
    
    def test_nlq_with_uploaded_data(self):
        """Test NLQ with uploaded CSV data"""
        # Create sample data
        df = pd.DataFrame({
            'Date': pd.date_range('2025-10-01', periods=10),
            'Region': ['Urban', 'Rural', 'Suburban'] * 3 + ['Urban'],
            'Revenue': [7000, 5000, 6000, 7100, 4900, 6100, 7200, 5100, 6200, 7300],
            'Units_Sold': [140, 80, 110, 142, 78, 112, 144, 82, 114, 146]
        })
        
        # Parse query
        query = "Team focused on urban but rural is growing"
        query_data = parse_nlq_intent(query)
        
        # Generate insights with uploaded data
        insights = generate_nlq_insights(query_data, df)
        self.assertGreater(len(insights), 0)
        
        print("✅ test_nlq_with_uploaded_data passed")
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        text = "Sales revenue growth profit opportunity market expansion strategy"
        keywords = extract_keywords(text, top_n=5)
        
        self.assertGreater(len(keywords), 0)
        self.assertLessEqual(len(keywords), 5)
        print("✅ test_extract_keywords passed")
    
    def test_detect_echo_chambers(self):
        """Test echo chamber detection"""
        text = "Premium is best. Premium customers are loyal. Premium margins are high. Premium is our focus. Premium is the future."
        echoes = detect_echo_chambers(text)
        
        self.assertGreater(len(echoes), 0)
        # 'premium' should be the top echo
        self.assertEqual(echoes[0]['keyword'], 'premium')
        self.assertGreaterEqual(echoes[0]['frequency'], 5)
        print("✅ test_detect_echo_chambers passed")
    
    def test_analyze_sentiment_basic(self):
        """Test sentiment analysis"""
        positive_text = "Great opportunity, excellent growth, amazing potential"
        negative_text = "Bad results, terrible performance, awful outcome"
        
        pos_score = analyze_sentiment_basic(positive_text)
        neg_score = analyze_sentiment_basic(negative_text)
        
        self.assertGreater(pos_score, 50)
        self.assertLess(neg_score, 50)
        print("✅ test_analyze_sentiment_basic passed")
    
    def test_monte_carlo_simulation(self):
        """Test Monte Carlo simulation"""
        df = pd.DataFrame({'Revenue': [5000, 5100, 5200, 5300, 5400, 5500]})
        
        sim_results = run_monte_carlo_simulation(df, bias_flip=False, n_runs=100)
        
        self.assertIsNotNone(sim_results)
        self.assertIn('mean', sim_results)
        self.assertIn('std', sim_results)
        self.assertGreater(len(sim_results['simulations']), 0)
        print("✅ test_monte_carlo_simulation passed")

class TestNLQEdgeCases(unittest.TestCase):
    """Test edge cases for NLQ Mode"""
    
    def test_vague_query(self):
        """Test handling of vague query"""
        query = "Help business?"
        result = parse_nlq_intent(query)
        
        self.assertIn(result['intent'], ['sales_issue', 'forecast', 'bias_check', 'general_advice'])
        print("✅ test_vague_query passed")
    
    def test_empty_query(self):
        """Test handling of empty query"""
        query = ""
        result = parse_nlq_intent(query)
        
        self.assertEqual(result['intent'], 'general_advice')
        print("✅ test_empty_query passed")
    
    def test_very_long_query(self):
        """Test handling of very long query"""
        query = "Sales " * 100 + "down"
        result = parse_nlq_intent(query)
        
        self.assertEqual(result['intent'], 'sales_issue')
        print("✅ test_very_long_query passed")
    
    def test_mixed_sentiment_query(self):
        """Test handling of mixed sentiment"""
        query = "Good growth but bad retention, excellent revenue but poor margins"
        result = parse_nlq_intent(query)
        
        self.assertIn(result['sentiment'], ['positive', 'negative', 'neutral'])
        print("✅ test_mixed_sentiment_query passed")

def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("🧪 RUNNING NARRATIVE NEXUS v1.2 NLQ MODE TESTS")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestNLQMode))
    suite.addTests(loader.loadTestsFromTestCase(TestNLQEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print(f"Tests run: {result.testsRun}")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
