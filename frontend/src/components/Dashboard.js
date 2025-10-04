import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  PieChart, 
  Target, 
  Zap,
  ArrowUpRight,
  ArrowDownRight,
  Brain,
  Smartphone,
  Menu,
  LogOut,
  Home,
  BarChart3,
  Receipt,
  CreditCard,
  Upload
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState(null);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generatingData, setGeneratingData] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, [user]);

  const loadDashboardData = async () => {
    try {
      // First, generate demo data if user doesn't have any
      setGeneratingData(true);
      await axios.post(`${API}/transactions/generate/${user.id}`);
      setGeneratingData(false);
      
      // Load summary data
      const summaryRes = await axios.get(`${API}/analytics/spending-summary/${user.id}`);
      setSummary(summaryRes.data);
      
      // Load trends data
      const trendsRes = await axios.get(`${API}/analytics/spending-trends/${user.id}`);
      setTrends(trendsRes.data);
      
      // Load recent insights
      const insightsRes = await axios.get(`${API}/ai/insights/${user.id}`);
      setInsights(insightsRes.data.slice(0, 3)); // Top 3 insights
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateAIInsights = async () => {
    try {
      setGeneratingData(true);
      await axios.post(`${API}/ai/insights/${user.id}`);
      
      // Reload insights
      const insightsRes = await axios.get(`${API}/ai/insights/${user.id}`);
      setInsights(insightsRes.data.slice(0, 3));
      
    } catch (error) {
      console.error('Error generating AI insights:', error);
    } finally {
      setGeneratingData(false);
    }
  };

  const sidebarItems = [
    { icon: Home, label: 'Dashboard', path: '/dashboard', active: true },
    { icon: BarChart3, label: 'Analytics', path: '/analytics' },
    { icon: Receipt, label: 'Transactions', path: '/transactions' },
    { icon: Upload, label: 'Import', path: '/import' },
    { icon: Brain, label: 'AI Insights', path:  '/insights' },
    { icon: CreditCard, label: 'Pay', path: '/pay' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          {generatingData && (
            <p className="text-slate-600">Setting up your personalized dashboard...</p>
          )}
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
              <h1 className="text-3xl font-bold text-slate-900 mb-2" data-testid="dashboard-title">
                Welcome back, {user.name}! 👋
              </h1>
              <p className="text-slate-600">
                Here's your financial overview for this month
              </p>
            </div>

            {/* Summary Cards */}
            {summary && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
                <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow card-hover" data-testid="total-expenses-card">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-slate-600">Total Expenses</CardTitle>
                    <TrendingDown className="h-4 w-4 text-red-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-slate-900">₹{summary.total_expenses.toLocaleString()}</div>
                    <p className="text-xs text-slate-600 mt-1">Last 30 days</p>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow card-hover" data-testid="total-income-card">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-slate-600">Total Income</CardTitle>
                    <TrendingUp className="h-4 w-4 text-green-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-slate-900">₹{summary.total_income.toLocaleString()}</div>
                    <p className="text-xs text-slate-600 mt-1">Last 30 days</p>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow card-hover" data-testid="net-savings-card">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-slate-600">Net Savings</CardTitle>
                    <Target className="h-4 w-4 text-blue-600" />
                  </CardHeader>
                  <CardContent>
                    <div className={`text-2xl font-bold ${
                      summary.net_savings >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      ₹{summary.net_savings.toLocaleString()}
                    </div>
                    <p className="text-xs text-slate-600 mt-1">
                      {summary.net_savings >= 0 ? 'Great job!' : 'Consider budgeting'}
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow card-hover" data-testid="invested-amount-card">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-slate-600">Invested Amount</CardTitle>
                    <DollarSign className="h-4 w-4 text-emerald-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-slate-900">₹{(summary.invested_amount ?? 0).toLocaleString()}</div>
                    <p className="text-xs text-slate-600 mt-1">
                      {summary.investment_transaction_count ? `${summary.investment_transaction_count} transactions` : 'Track your portfolio moves'}
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow card-hover" data-testid="transactions-count-card">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-slate-600">Transactions</CardTitle>
                    <Receipt className="h-4 w-4 text-purple-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-slate-900">{summary.transaction_count}</div>
                    <p className="text-xs text-slate-600 mt-1">This month</p>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Top Categories & AI Insights */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Top Spending Categories */}
              {summary && (
                <Card className="border-0 shadow-lg" data-testid="top-categories-card">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <PieChart className="h-5 w-5 text-blue-600" />
                      <span>Top Spending Categories</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {summary.top_categories.map((category, index) => (
                      <div key={index} className="flex items-center justify-between" data-testid={`category-${index}`}>
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${
                            index === 0 ? 'bg-blue-600' :
                            index === 1 ? 'bg-indigo-600' :
                            index === 2 ? 'bg-purple-600' :
                            index === 3 ? 'bg-pink-600' : 'bg-slate-400'
                          }`}></div>
                          <span className="font-medium text-slate-700">{category.category}</span>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold text-slate-900">₹{category.amount.toLocaleString()}</div>
                          <div className="text-sm text-slate-600">{category.percentage}%</div>
                        </div>
                      </div>
                    ))}
                    {summary.investment_category && !summary.top_categories.some((cat) => cat.category === 'Investments') && (
                      <div className="flex items-center justify-between border-t pt-4" data-testid="category-investments">
                        <div className="flex items-center space-x-3">
                          <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                          <span className="font-medium text-slate-700">{summary.investment_category.category}</span>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold text-slate-900">₹{summary.investment_category.amount.toLocaleString()}</div>
                          <div className="text-sm text-slate-600">{summary.investment_category.percentage}%</div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* AI Insights Preview */}
              <Card className="border-0 shadow-lg" data-testid="ai-insights-card">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center space-x-2">
                      <Brain className="h-5 w-5 text-indigo-600" />
                      <span>AI Insights</span>
                    </CardTitle>
                    <Button 
                      onClick={generateAIInsights}
                      disabled={generatingData}
                      size="sm" 
                      className="bg-gradient-to-r from-indigo-600 to-purple-700 hover:from-indigo-700 hover:to-purple-800"
                      data-testid="generate-insights-btn"
                    >
                      {generatingData ? (
                        <div className="flex items-center space-x-2">
                          <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                          <span>Analyzing...</span>
                        </div>
                      ) : (
                        <>
                          <Zap className="h-4 w-4 mr-1" />
                          Generate
                        </>
                      )}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {insights.length > 0 ? (
                    insights.map((insight, index) => (
                      <div key={index} className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg" data-testid={`insight-${index}`}>
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-semibold text-slate-900">{insight.title}</h4>
                          <Badge variant={insight.priority === 'high' ? 'destructive' : insight.priority === 'medium' ? 'default' : 'secondary'}>
                            {insight.priority}
                          </Badge>
                        </div>
                        <p className="text-sm text-slate-600 mb-2">{insight.description}</p>
                        <p className="text-sm font-medium text-indigo-700">{insight.recommendation}</p>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8" data-testid="no-insights">
                      <Brain className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                      <p className="text-slate-600 mb-4">No insights yet. Generate AI-powered recommendations!</p>
                      <Button 
                        onClick={generateAIInsights}
                        disabled={generatingData}
                        className="bg-gradient-to-r from-indigo-600 to-purple-700 hover:from-indigo-700 hover:to-purple-800"
                        data-testid="first-insights-btn"
                      >
                        Get Your First Insights
                      </Button>
                    </div>
                  )}
                  
                  {insights.length > 0 && (
                    <div className="pt-4 border-t">
                      <Link to="/insights">
                        <Button variant="outline" className="w-full" data-testid="view-all-insights-btn">
                          View All Insights
                          <ArrowUpRight className="h-4 w-4 ml-2" />
                        </Button>
                      </Link>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card className="border-0 shadow-lg" data-testid="quick-actions-card">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Link to="/transactions">
                    <Button variant="outline" className="w-full h-20 flex flex-col items-center justify-center space-y-2 hover:bg-blue-50 hover:border-blue-200" data-testid="view-transactions-btn">
                      <Receipt className="h-6 w-6 text-blue-600" />
                      <span className="text-sm font-medium">View Transactions</span>
                    </Button>
                  </Link>
                  
                  <Link to="/analytics">
                    <Button variant="outline" className="w-full h-20 flex flex-col items-center justify-center space-y-2 hover:bg-green-50 hover:border-green-200" data-testid="view-analytics-btn">
                      <BarChart3 className="h-6 w-6 text-green-600" />
                      <span className="text-sm font-medium">Analytics</span>
                    </Button>
                  </Link>
                  
                  <Link to="/pay">
                    <Button variant="outline" className="w-full h-20 flex flex-col items-center justify-center space-y-2 hover:bg-purple-50 hover:border-purple-200" data-testid="make-payment-btn">
                      <Smartphone className="h-6 w-6 text-purple-600" />
                      <span className="text-sm font-medium">Make Payment</span>
                    </Button>
                  </Link>
                  
                  <Link to="/insights">
                    <Button variant="outline" className="w-full h-20 flex flex-col items-center justify-center space-y-2 hover:bg-indigo-50 hover:border-indigo-200" data-testid="ai-insights-btn">
                      <Brain className="h-6 w-6 text-indigo-600" />
                      <span className="text-sm font-medium">AI Insights</span>
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
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

export default Dashboard;