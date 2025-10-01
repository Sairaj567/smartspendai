import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  Zap, 
  TrendingUp, 
  TrendingDown, 
  Target,
  Menu,
  LogOut,
  Home,
  BarChart3,
  Receipt,
  CreditCard,
  RefreshCw,
  Lightbulb,
  DollarSign,
  PieChart
} from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AIInsights = ({ user, onLogout }) => {
  const [insights, setInsights] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    loadInsights();
  }, [user]);

  const loadInsights = async () => {
    try {
      const [insightsRes, summaryRes] = await Promise.all([
        axios.get(`${API}/ai/insights/${user.id}`),
        axios.get(`${API}/analytics/spending-summary/${user.id}`)
      ]);
      
      setInsights(insightsRes.data);
      setSummary(summaryRes.data);
    } catch (error) {
      console.error('Error loading insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateNewInsights = async () => {
    try {
      setGenerating(true);
      await axios.post(`${API}/ai/insights/${user.id}`);
      
      // Reload insights
      const insightsRes = await axios.get(`${API}/ai/insights/${user.id}`);
      setInsights(insightsRes.data);
    } catch (error) {
      console.error('Error generating insights:', error);
    } finally {
      setGenerating(false);
    }
  };

  const sidebarItems = [
    { icon: Home, label: 'Dashboard', path: '/dashboard' },
    { icon: BarChart3, label: 'Analytics', path: '/analytics' },
    { icon: Receipt, label: 'Transactions', path: '/transactions' },
    { icon: Brain, label: 'AI Insights', path: '/insights', active: true },
    { icon: CreditCard, label: 'Pay', path: '/pay' }
  ];

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  const getInsightIcon = (type) => {
    switch (type) {
      case 'savings':
        return <Target className="h-5 w-5 text-green-600" />;
      case 'spending':
        return <TrendingDown className="h-5 w-5 text-red-600" />;
      case 'budgeting':
        return <PieChart className="h-5 w-5 text-blue-600" />;
      case 'optimization':
        return <TrendingUp className="h-5 w-5 text-purple-600" />;
      default:
        return <Lightbulb className="h-5 w-5 text-yellow-600" />;
    }
  };

  const getInsightGradient = (type) => {
    switch (type) {
      case 'savings':
        return 'from-green-50 to-emerald-50 border-green-200';
      case 'spending':
        return 'from-red-50 to-rose-50 border-red-200';
      case 'budgeting':
        return 'from-blue-50 to-indigo-50 border-blue-200';
      case 'optimization':
        return 'from-purple-50 to-violet-50 border-purple-200';
      default:
        return 'from-yellow-50 to-amber-50 border-yellow-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-slate-600">Loading AI insights...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Mobile Header */}
      <div className="lg:hidden bg-white shadow-sm border-b px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            data-testid="mobile-menu-btn"
          >
            <Menu className="h-5 w-5" />
          </Button>
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-lg text-slate-900">SpendSmart AI</span>
          </div>
        </div>
        <Button variant="ghost" size="sm" onClick={onLogout} data-testid="mobile-logout-btn">
          <LogOut className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transition-transform duration-300 ease-in-out`}>
          <div className="p-6">
            <div className="flex items-center space-x-2 mb-8">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <span className="font-bold text-xl text-slate-900">SpendSmart AI</span>
            </div>
            
            <nav className="space-y-2">
              {sidebarItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    item.active 
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-700 text-white' 
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                  data-testid={`sidebar-${item.label.toLowerCase().replace(' ', '-')}`}
                >
                  <item.icon className="h-5 w-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              ))}
            </nav>
          </div>
          
          {/* User Profile */}
          <div className="absolute bottom-0 left-0 right-0 p-6 border-t">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-semibold">{user.name[0]}</span>
              </div>
              <div>
                <p className="font-medium text-slate-900">{user.name}</p>
                <p className="text-sm text-slate-600">{user.email}</p>
              </div>
            </div>
            <Button 
              onClick={onLogout} 
              variant="outline" 
              className="w-full"
              data-testid="sidebar-logout-btn"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 lg:ml-0">
          <div className="p-6">
            {/* Header */}
            <div className="mb-8">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-slate-900 mb-2" data-testid="insights-title">
                    AI Financial Insights 🤖
                  </h1>
                  <p className="text-slate-600">
                    Powered by Gemini 2.5 Pro - Get personalized financial advice
                  </p>
                </div>
                
                <Button 
                  onClick={generateNewInsights}
                  disabled={generating}
                  className="mt-4 sm:mt-0 bg-gradient-to-r from-indigo-600 to-purple-700 hover:from-indigo-700 hover:to-purple-800"
                  data-testid="generate-insights-btn"
                >
                  {generating ? (
                    <div className="flex items-center space-x-2">
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      <span>Analyzing...</span>
                    </div>
                  ) : (
                    <>
                      <Zap className="h-4 w-4 mr-2" />
                      Generate New Insights
                    </>
                  )}
                </Button>
              </div>
            </div>

            {/* Quick Stats */}
            {summary && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <Card className="border-0 shadow-lg" data-testid="insights-stats-expenses">
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-lg flex items-center justify-center">
                        <TrendingDown className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <p className="text-sm text-slate-600 mb-1">Monthly Expenses</p>
                        <p className="text-2xl font-bold text-slate-900">₹{summary.total_expenses.toLocaleString()}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-lg" data-testid="insights-stats-savings">
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4">
                      <div className={`w-12 h-12 bg-gradient-to-br ${summary.net_savings >= 0 ? 'from-green-500 to-green-600' : 'from-red-500 to-red-600'} rounded-lg flex items-center justify-center`}>
                        <Target className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <p className="text-sm text-slate-600 mb-1">Net Savings</p>
                        <p className={`text-2xl font-bold ${summary.net_savings >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          ₹{summary.net_savings.toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-lg" data-testid="insights-stats-transactions">
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                        <Receipt className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <p className="text-sm text-slate-600 mb-1">Transactions</p>
                        <p className="text-2xl font-bold text-slate-900">{summary.transaction_count}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* AI Insights */}
            {insights.length === 0 ? (
              <Card className="border-0 shadow-lg" data-testid="no-insights-card">
                <CardContent className="p-12 text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Brain className="h-8 w-8 text-indigo-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-900 mb-4">No Insights Generated Yet</h3>
                  <p className="text-slate-600 mb-6">
                    Let our AI analyze your spending patterns and provide personalized financial recommendations.
                  </p>
                  <Button 
                    onClick={generateNewInsights}
                    disabled={generating}
                    size="lg"
                    className="bg-gradient-to-r from-indigo-600 to-purple-700 hover:from-indigo-700 hover:to-purple-800"
                    data-testid="first-insights-btn"
                  >
                    {generating ? (
                      <div className="flex items-center space-x-2">
                        <RefreshCw className="h-5 w-5 animate-spin" />
                        <span>Generating Your First Insights...</span>
                      </div>
                    ) : (
                      <>
                        <Zap className="h-5 w-5 mr-2" />
                        Generate Your First Insights
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-6">
                {insights.map((insight, index) => (
                  <Card 
                    key={index} 
                    className={`border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-r ${getInsightGradient(insight.insight_type)} border`}
                    data-testid={`insight-${index}`}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-white/80 rounded-lg flex items-center justify-center">
                            {getInsightIcon(insight.insight_type)}
                          </div>
                          <div>
                            <h3 className="text-xl font-semibold text-slate-900">{insight.title}</h3>
                            <p className="text-sm text-slate-600 capitalize">{insight.insight_type} Insight</p>
                          </div>
                        </div>
                        <Badge className={getPriorityColor(insight.priority)}>
                          {insight.priority} priority
                        </Badge>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="p-4 bg-white/60 rounded-lg">
                          <h4 className="font-medium text-slate-900 mb-2">Analysis</h4>
                          <p className="text-slate-700">{insight.description}</p>
                        </div>
                        
                        <div className="p-4 bg-white/60 rounded-lg">
                          <h4 className="font-medium text-slate-900 mb-2 flex items-center">
                            <Lightbulb className="h-4 w-4 mr-2 text-yellow-600" />
                            Recommendation
                          </h4>
                          <p className="text-slate-700 font-medium">{insight.recommendation}</p>
                        </div>
                        
                        <div className="text-xs text-slate-500">
                          Generated on {new Date(insight.created_at).toLocaleDateString('en-IN', {
                            day: 'numeric',
                            month: 'long',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}

            {/* Action Cards */}
            {insights.length > 0 && (
              <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="border-0 shadow-lg" data-testid="action-analytics">
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4 mb-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                        <BarChart3 className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-900">Detailed Analytics</h3>
                        <p className="text-sm text-slate-600">View comprehensive spending analysis</p>
                      </div>
                    </div>
                    <Link to="/analytics">
                      <Button variant="outline" className="w-full" data-testid="view-analytics-btn">
                        View Analytics Dashboard
                      </Button>
                    </Link>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-lg" data-testid="action-transactions">
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4 mb-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
                        <Receipt className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-900">Transaction History</h3>
                        <p className="text-sm text-slate-600">Review your recent transactions</p>
                      </div>
                    </div>
                    <Link to="/transactions">
                      <Button variant="outline" className="w-full" data-testid="view-transactions-btn">
                        View All Transactions
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden" 
          onClick={() => setSidebarOpen(false)}
          data-testid="sidebar-overlay"
        ></div>
      )}
    </div>
  );
};

export default AIInsights;