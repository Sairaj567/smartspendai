import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  Smartphone, 
  Brain, 
  Shield, 
  PieChart, 
  Zap,
  CheckCircle,
  Star,
  ArrowRight
} from 'lucide-react';

const LandingPage = ({ onGetStarted }) => {
  const features = [
    {
      icon: <Brain className="h-6 w-6" />,
      title: 'AI-Powered Insights',
      description: 'Get personalized spending analysis and smart recommendations from Gemini 2.5 Pro'
    },
    {
      icon: <PieChart className="h-6 w-6" />,
      title: 'Visual Analytics',
      description: 'Beautiful charts and trends that make your financial data easy to understand'
    },
    {
      icon: <Smartphone className="h-6 w-6" />,
      title: 'UPI Integration',
      description: 'Seamless payments through Google Pay, PhonePe, Paytm, and other UPI apps'
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: 'Bank-Grade Security',
      description: 'Your financial data is protected with enterprise-level encryption'
    },
    {
      icon: <TrendingUp className="h-6 w-6" />,
      title: 'Smart Budgeting',
      description: 'Automated budget tracking with intelligent alerts and recommendations'
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: 'Real-time Updates',
      description: 'Instant transaction categorization and spending analysis'
    }
  ];

  const testimonials = [
    {
      name: 'Priya Sharma',
      role: 'Software Engineer',
      content: 'SpendSmart AI helped me save ₹15,000 in just 2 months with its smart insights!',
      rating: 5
    },
    {
      name: 'Rahul Patel',
      role: 'Business Owner',
      content: 'The AI recommendations are spot-on. Perfect for managing both personal and business expenses.',
      rating: 5
    },
    {
      name: 'Anita Singh',
      role: 'Marketing Manager',
      content: 'Love the UPI integration! Makes tracking payments so much easier.',
      rating: 5
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-slate-200 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center">
                <Brain className="h-5 w-5 text-white" />
              </div>
              <span className="font-bold text-xl text-slate-900">SpendSmart AI</span>
            </div>
            <Button 
              onClick={onGetStarted}
              data-testid="get-started-btn"
              className="bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-white px-6 py-2 rounded-lg font-medium transition-all duration-200 hover:shadow-lg"
            >
              Get Started
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="space-y-4">
              
                <h1 className="text-5xl lg:text-6xl font-bold text-slate-900 leading-tight">
                  Smart Money,
                  <span className="bg-gradient-to-r from-blue-600 to-indigo-700 bg-clip-text text-transparent">
                    {' '}Smarter Decisions
                  </span>
                </h1>
                <p className="text-xl text-slate-600 leading-relaxed">
                  Experience the future of personal finance with AI-powered insights, seamless UPI payments, and intelligent budgeting that adapts to your lifestyle.
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <Button 
                  onClick={onGetStarted}
                  data-testid="hero-get-started-btn"
                  size="lg"
                  className="bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-white px-8 py-4 text-lg font-semibold rounded-lg transition-all duration-200 hover:shadow-xl hover:scale-105"
                >
                  Start Your Journey
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
                <Button 
                  variant="outline" 
                  size="lg"
                  className="border-2 border-slate-300 text-slate-700 hover:bg-slate-50 px-8 py-4 text-lg font-semibold rounded-lg transition-all duration-200"
                >
                  View Demo
                </Button>
              </div>

              <div className="flex items-center space-x-6 text-sm text-slate-600">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Free to start</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Bank-grade security</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>AI-powered</span>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-3xl transform rotate-3 opacity-20"></div>
              <Card className="relative bg-white/90 backdrop-blur-sm border-0 shadow-2xl rounded-3xl overflow-hidden">
                <CardContent className="p-0">
                  <img 
                    src="https://images.unsplash.com/photo-1748439435495-722cc1728b7e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHwxfHxmaW50ZWNoJTIwZGFzaGJvYXJkfGVufDB8fHx8MTc1ODg4MjcyNnww&ixlib=rb-4.1.0&q=85" 
                    alt="SpendSmart AI Dashboard" 
                    className="w-full h-96 object-cover"
                  />
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-4xl font-bold text-slate-900">Powerful Features</h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Everything you need to take control of your finances, powered by cutting-edge AI technology
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 bg-gradient-to-br from-white to-slate-50">
                <CardContent className="p-8">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center text-white">
                      {feature.icon}
                    </div>
                    <h3 className="text-xl font-semibold text-slate-900">{feature.title}</h3>
                  </div>
                  <p className="text-slate-600 leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Visual Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="space-y-8">
              <div className="space-y-4">
                <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
                  AI Analytics
                </Badge>
                <h2 className="text-4xl font-bold text-slate-900">
                  Intelligent Spending
                  <span className="block text-blue-600">Analysis</span>
                </h2>
                <p className="text-lg text-slate-600">
                  Our AI analyzes your spending patterns, identifies trends, and provides actionable insights to help you save more and spend smarter.
                </p>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-slate-700">Automatic transaction categorization</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-slate-700">Personalized spending recommendations</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-slate-700">Predictive budget alerts</span>
                </div>
              </div>
            </div>

            <div className="relative">
              <img 
                src="https://images.unsplash.com/photo-1748439281934-2803c6a3ee36?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHwyfHxmaW50ZWNoJTIwZGFzaGJvYXJkfGVufDB8fHx8MTc1ODg4MjcyNnww&ixlib=rb-4.1.0&q=85" 
                alt="Financial Analytics" 
                className="rounded-2xl shadow-2xl w-full"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Mobile Features */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="order-2 lg:order-1">
              <img 
                src="https://images.unsplash.com/photo-1681826291722-70bd7e9e6fc3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzh8MHwxfHNlYXJjaHwxfHxtb2JpbGUlMjBiYW5raW5nfGVufDB8fHx8MTc1ODk4MTE5NHww&ixlib=rb-4.1.0&q=85" 
                alt="Mobile Banking" 
                className="rounded-2xl shadow-2xl w-full"
              />
            </div>
            
            <div className="space-y-8 order-1 lg:order-2">
              <div className="space-y-4">
                <Badge className="bg-indigo-100 text-indigo-800 hover:bg-indigo-100">
                  UPI Integration
                </Badge>
                <h2 className="text-4xl font-bold text-slate-900">
                  Seamless
                  <span className="block text-indigo-600">Payments</span>
                </h2>
                <p className="text-lg text-slate-600">
                  Pay instantly through Google Pay, PhonePe, Paytm, or any UPI app. Track every transaction automatically with smart categorization.
                </p>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-slate-700">Instant UPI payments</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-slate-700">Automatic transaction tracking</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-slate-700">Secure payment processing</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-4xl font-bold text-slate-900">What Our Users Say</h2>
            <p className="text-xl text-slate-600">
              Join thousands of satisfied users who've transformed their financial habits
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="border-0 shadow-lg bg-white">
                <CardContent className="p-8">
                  <div className="flex items-center space-x-1 mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="text-slate-600 mb-6 italic">"{testimonial.content}"</p>
                  <div className="border-t pt-4">
                    <p className="font-semibold text-slate-900">{testimonial.name}</p>
                    <p className="text-sm text-slate-600">{testimonial.role}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-600 to-indigo-700">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <h2 className="text-4xl lg:text-5xl font-bold text-white">
            Ready to Transform Your Finances?
          </h2>
          <p className="text-xl text-blue-100">
            Join thousands of users who are already saving more and spending smarter with SpendSmart AI
          </p>
          <Button 
            onClick={onGetStarted}
            data-testid="cta-get-started-btn"
            size="lg"
            className="bg-white text-blue-600 hover:bg-blue-50 px-8 py-4 text-lg font-semibold rounded-lg transition-all duration-200 hover:shadow-xl hover:scale-105"
          >
            Get Started Free
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center space-x-2 mb-8">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-xl">SpendSmart AI</span>
          </div>
          <div className="text-center space-y-4">
            <p className="text-slate-400">
              Built with ❤️ by Team Tripod for the future of personal finance
            </p>
            <p className="text-sm text-slate-500">
              © 2025 SpendSmart AI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;