import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  CreditCard, 
  Smartphone, 
  QrCode, 
  Shield,
  Brain,
  Menu,
  LogOut,
  Home,
  BarChart3,
  Receipt,
  CheckCircle,
  AlertCircle,
  Loader2,
  ArrowRight,
  Copy,
  ExternalLink
} from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PaymentFlow = ({ user, onLogout }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [paymentData, setPaymentData] = useState({
    amount: '',
    payee_name: '',
    payee_vpa: '',
    description: ''
  });
  const [paymentStatus, setPaymentStatus] = useState('idle'); // idle, processing, success, error
  const [paymentResult, setPaymentResult] = useState(null);
  const [recentPayments, setRecentPayments] = useState([]);
  const [validationErrors, setValidationErrors] = useState({});

  // Fallback demo user if no user is provided (for testing)
  const effectiveUser = user || {
    id: 'demo_user_123',
    name: 'Demo User',
    email: 'demo@spendsmart.ai',
    phone: '+91 9876543210'
  };

  const sidebarItems = [
    { icon: Home, label: 'Dashboard', path: '/dashboard' },
    { icon: BarChart3, label: 'Analytics', path: '/analytics' },
    { icon: Receipt, label: 'Transactions', path: '/transactions' },
    { icon: Brain, label: 'AI Insights', path: '/insights' },
    { icon: CreditCard, label: 'Pay', path: '/pay', active: true }
  ];

  const upiApps = [
    { name: 'Google Pay', icon: '🌐', color: 'from-blue-500 to-blue-600' },
    { name: 'PhonePe', icon: '📱', color: 'from-purple-500 to-purple-600' },
    { name: 'Paytm', icon: '💳', color: 'from-indigo-500 to-indigo-600' },
    { name: 'BHIM', icon: '🇮🇳', color: 'from-orange-500 to-orange-600' }
  ];

  const quickAmounts = [100, 500, 1000, 2000, 5000];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setPaymentData({
      ...paymentData,
      [name]: value
    });
    
    // Clear validation error for this field when user starts typing
    if (validationErrors[name]) {
      setValidationErrors({
        ...validationErrors,
        [name]: undefined
      });
    }
  };

  const setQuickAmount = (amount) => {
    setPaymentData({
      ...paymentData,
      amount: amount.toString()
    });
  };

  const generateUPIPayment = async (e) => {
    e.preventDefault();
    
    // Reset validation errors
    setValidationErrors({});
    
    // Validate form data
    const errors = {};
    if (!paymentData.amount || parseFloat(paymentData.amount) <= 0) {
      errors.amount = 'Please enter a valid amount';
    }
    if (!paymentData.payee_name.trim()) {
      errors.payee_name = 'Please enter payee name';
    }
    if (!paymentData.payee_vpa.trim()) {
      errors.payee_vpa = 'Please enter UPI ID or phone number';
    }
    
    // Check if backend URL is configured
    if (!BACKEND_URL) {
      errors.general = 'Backend service is not configured. Please check environment variables.';
    }
    
    // Check if user is properly authenticated
    if (!effectiveUser || !effectiveUser.id) {
      errors.general = 'User session is invalid. Please log in again.';
    }
    
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    setPaymentStatus('processing');
    
    console.log('Making payment request to:', `${API}/payments/upi-intent`);
    console.log('BACKEND_URL:', BACKEND_URL);
    console.log('API:', API);
    console.log('Payment data:', { ...paymentData, amount: parseFloat(paymentData.amount), user_id: effectiveUser.id });
    
    try {
      const response = await axios.post(`${API}/payments/upi-intent`, {
        ...paymentData,
        amount: parseFloat(paymentData.amount),
        user_id: effectiveUser.id
      });
      
      setPaymentResult(response.data);
      setPaymentStatus('success');
      
      // Simulate opening UPI app (in real implementation, this would redirect)
      setTimeout(() => {
        // Mock payment success after 3 seconds
        simulatePaymentCallback(response.data.transaction_id, 'success');
      }, 3000);
      
    } catch (error) {
      console.error('Payment error:', error);
      console.error('Error details:', error.response?.data);
      console.error('Error status:', error.response?.status);
      console.error('Error message:', error.message);
      setPaymentStatus('error');
      setPaymentResult({ error: `Failed to create payment request: ${error.message}` });
    }
  };

  const simulatePaymentCallback = async (transactionId, status) => {
    try {
      await axios.post(`${API}/payments/callback/${transactionId}?status=${status}`);
      
      if (status === 'success') {
        setPaymentStatus('completed');
        // Reset form
        setPaymentData({
          amount: '',
          payee_name: '',
          payee_vpa: '',
          description: ''
        });
      } else {
        setPaymentStatus('error');
        setPaymentResult({ error: 'Payment was cancelled or failed' });
      }
    } catch (error) {
      console.error('Callback error:', error);
    }
  };

  const resetPayment = () => {
    setPaymentStatus('idle');
    setPaymentResult(null);
  };

  const copyUPILink = () => {
    if (paymentResult?.upi_url) {
      navigator.clipboard.writeText(paymentResult.upi_url);
    }
  };

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
                <span className="text-white font-semibold">{effectiveUser.name[0]}</span>
              </div>
              <div>
                <p className="font-medium text-slate-900">{effectiveUser.name}</p>
                <p className="text-sm text-slate-600">{effectiveUser.email}</p>
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
              <h1 className="text-3xl font-bold text-slate-900 mb-2" data-testid="payment-title">
                UPI Payments 📱
              </h1>
              <p className="text-slate-600">
                Send money instantly to anyone using UPI
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Payment Form */}
              <div className="space-y-6">
                {paymentStatus === 'idle' && (
                  <Card className="border-0 shadow-lg" data-testid="payment-form-card">
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <CreditCard className="h-5 w-5 text-blue-600" />
                        <span>Send Money</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <form onSubmit={generateUPIPayment} className="space-y-6">
                        {/* General Error */}
                        {validationErrors.general && (
                          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                            <p className="text-sm text-red-600">{validationErrors.general}</p>
                          </div>
                        )}
                        
                        {/* Amount */}
                        <div className="space-y-2">
                          <Label htmlFor="amount">Amount (₹)</Label>
                          <Input
                            id="amount"
                            name="amount"
                            type="number"
                            placeholder="Enter amount"
                            value={paymentData.amount}
                            onChange={handleInputChange}
                            className={`text-2xl font-bold h-14 ${validationErrors.amount ? 'border-red-500' : ''}`}
                            required
                            data-testid="amount-input"
                          />
                          {validationErrors.amount && (
                            <p className="text-sm text-red-600">{validationErrors.amount}</p>
                          )}
                          
                          {/* Quick Amount Buttons */}
                          <div className="flex flex-wrap gap-2 mt-3">
                            {quickAmounts.map(amount => (
                              <Button
                                key={amount}
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => setQuickAmount(amount)}
                                data-testid={`quick-amount-${amount}`}
                              >
                                ₹{amount.toLocaleString()}
                              </Button>
                            ))}
                          </div>
                        </div>

                        {/* Payee Details */}
                        <div className="grid grid-cols-1 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="payee_name">Payee Name</Label>
                            <Input
                              id="payee_name"
                              name="payee_name"
                              placeholder="Enter payee name"
                              value={paymentData.payee_name}
                              onChange={handleInputChange}
                              className={validationErrors.payee_name ? 'border-red-500' : ''}
                              required
                              data-testid="payee-name-input"
                            />
                            {validationErrors.payee_name && (
                              <p className="text-sm text-red-600">{validationErrors.payee_name}</p>
                            )}
                          </div>
                          
                          <div className="space-y-2">
                            <Label htmlFor="payee_vpa">UPI ID / Phone Number</Label>
                            <Input
                              id="payee_vpa"
                              name="payee_vpa"
                              placeholder="name@upi or 9876543210"
                              value={paymentData.payee_vpa}
                              onChange={handleInputChange}
                              className={validationErrors.payee_vpa ? 'border-red-500' : ''}
                              required
                              data-testid="payee-vpa-input"
                            />
                            {validationErrors.payee_vpa && (
                              <p className="text-sm text-red-600">{validationErrors.payee_vpa}</p>
                            )}
                          </div>
                        </div>

                        {/* Description */}
                        <div className="space-y-2">
                          <Label htmlFor="description">Description (Optional)</Label>
                          <Input
                            id="description"
                            name="description"
                            placeholder="Payment for..."
                            value={paymentData.description}
                            onChange={handleInputChange}
                            data-testid="description-input"
                          />
                        </div>

                        {/* Submit Button */}
                        <Button 
                          type="submit" 
                          className="w-full h-12 bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-lg font-semibold"
                          data-testid="pay-now-btn"
                        >
                          <Smartphone className="h-5 w-5 mr-2" />
                          Pay Now
                        </Button>
                      </form>
                    </CardContent>
                  </Card>
                )}

                {/* Payment Processing */}
                {paymentStatus === 'processing' && (
                  <Card className="border-0 shadow-lg" data-testid="payment-processing-card">
                    <CardContent className="p-8 text-center">
                      <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                        <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
                      </div>
                      <h3 className="text-xl font-semibold text-slate-900 mb-2">Creating Payment Request...</h3>
                      <p className="text-slate-600">Please wait while we prepare your UPI payment</p>
                    </CardContent>
                  </Card>
                )}

                {/* Payment Success */}
                {paymentStatus === 'success' && paymentResult && (
                  <Card className="border-0 shadow-lg border-l-4 border-l-blue-600" data-testid="payment-success-card">
                    <CardContent className="p-6">
                      <div className="flex items-start space-x-4">
                        <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                          <QrCode className="h-6 w-6 text-blue-600" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-slate-900 mb-2">UPI Payment Ready!</h3>
                          <p className="text-slate-600 mb-4">Transaction ID: {paymentResult.transaction_id}</p>
                          
                          <div className="space-y-3">
                            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                              <span className="text-sm text-slate-600">UPI Link:</span>
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                onClick={copyUPILink}
                                data-testid="copy-upi-link-btn"
                              >
                                <Copy className="h-4 w-4" />
                              </Button>
                            </div>
                            
                            <Button 
                              className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800"
                              onClick={() => window.open(paymentResult.upi_url, '_blank')}
                              data-testid="open-upi-app-btn"
                            >
                              <ExternalLink className="h-4 w-4 mr-2" />
                              Open in UPI App
                            </Button>
                          </div>
                          
                          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                            <p className="text-sm text-blue-800">
                              🔄 Simulating payment... This will complete automatically in a few seconds.
                            </p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Payment Completed */}
                {paymentStatus === 'completed' && (
                  <Card className="border-0 shadow-lg border-l-4 border-l-green-600" data-testid="payment-completed-card">
                    <CardContent className="p-6">
                      <div className="text-center">
                        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                          <CheckCircle className="h-8 w-8 text-green-600" />
                        </div>
                        <h3 className="text-xl font-semibold text-slate-900 mb-2">Payment Successful!</h3>
                        <p className="text-slate-600 mb-6">
                          ₹{paymentData.amount} sent successfully to {paymentData.payee_name}
                        </p>
                        <Button 
                          onClick={resetPayment}
                          className="bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800"
                          data-testid="make-another-payment-btn"
                        >
                          Make Another Payment
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Payment Error */}
                {paymentStatus === 'error' && (
                  <Card className="border-0 shadow-lg border-l-4 border-l-red-600" data-testid="payment-error-card">
                    <CardContent className="p-6">
                      <div className="flex items-start space-x-4">
                        <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                          <AlertCircle className="h-6 w-6 text-red-600" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-slate-900 mb-2">Payment Failed</h3>
                          <p className="text-slate-600 mb-4">
                            {paymentResult?.error || 'Something went wrong. Please try again.'}
                          </p>
                          <Button 
                            onClick={resetPayment}
                            variant="outline"
                            data-testid="try-again-btn"
                          >
                            Try Again
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Right Column - UPI Apps & Info */}
              <div className="space-y-6">
                {/* UPI Apps */}
                <Card className="border-0 shadow-lg" data-testid="upi-apps-card">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Smartphone className="h-5 w-5 text-purple-600" />
                      <span>Supported UPI Apps</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                      {upiApps.map((app, index) => (
                        <div 
                          key={index} 
                          className={`p-4 bg-gradient-to-br ${app.color} rounded-lg text-white text-center`}
                          data-testid={`upi-app-${index}`}
                        >
                          <div className="text-2xl mb-2">{app.icon}</div>
                          <div className="font-medium">{app.name}</div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Security Info */}
                <Card className="border-0 shadow-lg" data-testid="security-info-card">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Shield className="h-5 w-5 text-green-600" />
                      <span>Secure Payments</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-start space-x-3">
                      <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                      <div>
                        <p className="font-medium text-slate-900">Bank-Grade Security</p>
                        <p className="text-sm text-slate-600">All transactions are encrypted and secure</p>
                      </div>
                    </div>
                    
                    <div className="flex items-start space-x-3">
                      <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                      <div>
                        <p className="font-medium text-slate-900">RBI Compliant</p>
                        <p className="text-sm text-slate-600">Follows all regulatory guidelines</p>
                      </div>
                    </div>
                    
                    <div className="flex items-start space-x-3">
                      <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                      <div>
                        <p className="font-medium text-slate-900">Instant Transfers</p>
                        <p className="text-sm text-slate-600">Money reaches instantly 24/7</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Quick Actions */}
                <Card className="border-0 shadow-lg" data-testid="quick-actions-card">
                  <CardHeader>
                    <CardTitle>Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <Link to="/transactions">
                        <Button variant="outline" className="w-full justify-start" data-testid="view-payment-history-btn">
                          <Receipt className="h-4 w-4 mr-2" />
                          View Payment History
                        </Button>
                      </Link>
                      
                      <Link to="/analytics">
                        <Button variant="outline" className="w-full justify-start" data-testid="spending-analytics-btn">
                          <BarChart3 className="h-4 w-4 mr-2" />
                          Spending Analytics
                        </Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
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

export default PaymentFlow;