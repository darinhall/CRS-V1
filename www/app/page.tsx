import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Camera, BookOpen, Users, Search, Zap, Target } from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Camera className="h-8 w-8 text-secondary" />
              <span className="text-2xl font-bold text-foreground">Altoscope</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#database" className="text-muted-foreground hover:text-foreground transition-colors">
                Database
              </a>
              <a href="#guides" className="text-muted-foreground hover:text-foreground transition-colors">
                Guides
              </a>
              <a href="#community" className="text-muted-foreground hover:text-foreground transition-colors">
                Community
              </a>
              <Button variant="outline" size="sm">
                Sign In
              </Button>
              <Button size="sm" className="bg-secondary text-secondary-foreground hover:bg-secondary/90">
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <Badge variant="secondary" className="mb-6 bg-secondary/10 text-secondary border-secondary/20">
              Knowledge Hub for Visual Creators
            </Badge>
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-balance mb-6">
              Empower your vision with <span className="text-secondary">comprehensive</span> camera knowledge.
            </h1>
            <p className="text-xl text-muted-foreground text-balance max-w-3xl mx-auto mb-8">
              Discover, research, and master professional camera equipment through the industry's most robust database
              and educational resources. From concept to completion, we support every creative workflow.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-secondary text-secondary-foreground hover:bg-secondary/90">
                Explore the Hub
              </Button>
              <Button variant="outline" size="lg">
                View Database
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 border-y border-border">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-secondary mb-2">10,000+</div>
              <div className="text-muted-foreground">Equipment Specs</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-secondary mb-2">500+</div>
              <div className="text-muted-foreground">Learning Guides</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-secondary mb-2">50,000+</div>
              <div className="text-muted-foreground">Visual Creators</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-secondary mb-2">99%</div>
              <div className="text-muted-foreground">Accuracy Rate</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="database" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Everything you need to make informed decisions</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Our comprehensive platform combines detailed specifications, educational content, and community insights.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="bg-card border-border">
              <CardContent className="p-6">
                <Search className="h-12 w-12 text-secondary mb-4" />
                <h3 className="text-xl font-bold mb-2">Comprehensive Database</h3>
                <p className="text-muted-foreground">
                  Access detailed specifications for thousands of cameras, lenses, and accessories from every major
                  manufacturer.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardContent className="p-6">
                <BookOpen className="h-12 w-12 text-secondary mb-4" />
                <h3 className="text-xl font-bold mb-2">Educational Guides</h3>
                <p className="text-muted-foreground">
                  Learn from expert tutorials, comparison guides, and in-depth reviews to master your craft.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardContent className="p-6">
                <Users className="h-12 w-12 text-secondary mb-4" />
                <h3 className="text-xl font-bold mb-2">Community Insights</h3>
                <p className="text-muted-foreground">
                  Connect with fellow creators, share experiences, and get recommendations from the community.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardContent className="p-6">
                <Zap className="h-12 w-12 text-secondary mb-4" />
                <h3 className="text-xl font-bold mb-2">Smart Comparisons</h3>
                <p className="text-muted-foreground">
                  Compare equipment side-by-side with intelligent filtering and recommendation algorithms.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardContent className="p-6">
                <Target className="h-12 w-12 text-secondary mb-4" />
                <h3 className="text-xl font-bold mb-2">Project Planning</h3>
                <p className="text-muted-foreground">
                  Plan your shoots with equipment recommendations based on your specific project requirements.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardContent className="p-6">
                <Camera className="h-12 w-12 text-secondary mb-4" />
                <h3 className="text-xl font-bold mb-2">Latest Updates</h3>
                <p className="text-muted-foreground">
                  Stay current with the latest equipment releases, firmware updates, and industry trends.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-primary/5">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to elevate your creative workflow?</h2>
          <p className="text-xl text-muted-foreground mb-8">
            Join thousands of visual creators who trust Altoscope for their equipment research and education.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-secondary text-secondary-foreground hover:bg-secondary/90">
              Start Exploring
            </Button>
            <Button variant="outline" size="lg">
              View Pricing
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Camera className="h-6 w-6 text-secondary" />
                <span className="text-lg font-bold">Altoscope</span>
              </div>
              <p className="text-muted-foreground">
                Empowering visual creators through comprehensive camera equipment knowledge and education.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Platform</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li>
                  <a href="#" className="hover:text-foreground transition-colors">
                    Database
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground transition-colors">
                    Guides
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground transition-colors">
                    Comparisons
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground transition-colors">
                    Reviews
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Community</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li>
                  <a href="#" className="hover:text-foreground transition-colors">
                    Forums
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground transition-colors">
                    Contributors
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground transition-colors">
                    Events
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground transition-colors">
                    Newsletter
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li>
                  <a href="#" className="hover:text-foreground transition-colors">
                    About
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground transition-colors">
                    Careers
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground transition-colors">
                    Contact
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground transition-colors">
                    Privacy
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-border mt-8 pt-8 text-center text-muted-foreground">
            <p>&copy; 2024 Altoscope. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
