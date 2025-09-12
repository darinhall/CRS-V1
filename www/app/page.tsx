import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Camera, Search, Users, ShoppingCart, Star, ArrowRight, Database, MapPin } from "lucide-react"
import Link from "next/link"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background dark">
      {/* Header */}
      <header className="border-b border-border/50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Camera className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold text-foreground">Altoscope</span>
          </div>
          <nav className="hidden md:flex items-center space-x-6">
            <Link href="#features" className="text-muted-foreground hover:text-foreground transition-colors">
              Features
            </Link>
            <Link href="#marketplace" className="text-muted-foreground hover:text-foreground transition-colors">
              Marketplace
            </Link>
            <Link href="/explore" className="text-muted-foreground hover:text-foreground transition-colors">
              Explore
            </Link>
            <Button variant="outline" size="sm">
              Sign In
            </Button>
            <Button size="sm">Get Started</Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 lg:py-32 overflow-hidden">
        <div className="absolute inset-0 gradient-bg" />
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-accent/5 to-primary/10" />
        <div className="container mx-auto px-4 relative">
          <div className="max-w-4xl mx-auto text-center">
            <Badge variant="secondary" className="mb-6 glow-effect">
              Trusted by 10,000+ Visual Creators
            </Badge>
            <h1 className="text-4xl lg:text-6xl font-bold text-balance mb-6">
              The Ultimate Platform for <span className="gradient-text">Camera Equipment</span>
            </h1>
            <p className="text-xl text-muted-foreground text-balance mb-8 max-w-2xl mx-auto">
              Discover, research, and rent professional camera gear. Connect with rental houses, studios, and fellow
              creators in one comprehensive ecosystem.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Button size="lg" className="text-lg px-8 glow-effect">
                Explore Equipment
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button variant="outline" size="lg" className="text-lg px-8 bg-transparent border-primary/50 hover:bg-primary/10">
                Browse Rentals
              </Button>
            </div>

            {/* Search Bar */}
            <div className="max-w-2xl mx-auto">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-muted-foreground h-5 w-5" />
                <Input
                  placeholder="Search cameras, lenses, lighting equipment..."
                  className="pl-12 h-14 text-lg bg-card/50 border-2 border-primary/30 backdrop-blur-sm"
                />
                <Button className="absolute right-2 top-2 h-10 glow-effect">Search</Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-muted/20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4">Everything You Need in One Platform</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              From comprehensive gear databases to seamless rentals, we've built the tools visual creators need.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="card-gradient float-animation">
              <CardHeader>
                <Database className="h-12 w-12 text-primary mb-4 glow-effect" />
                <CardTitle>Comprehensive Database</CardTitle>
                <CardDescription>
                  Access detailed specifications, reviews, and comparisons for thousands of professional cameras,
                  lenses, and accessories.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="card-gradient float-animation" style={{ animationDelay: '0.5s' }}>
              <CardHeader>
                <ShoppingCart className="h-12 w-12 text-accent mb-4 glow-effect" />
                <CardTitle>Rental Marketplace</CardTitle>
                <CardDescription>
                  Connect with verified rental houses and individual owners. Book equipment with confidence and
                  transparent pricing.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="card-gradient float-animation" style={{ animationDelay: '1s' }}>
              <CardHeader>
                <Users className="h-12 w-12 text-primary mb-4 glow-effect" />
                <CardTitle>Creator Community</CardTitle>
                <CardDescription>
                  Join a vibrant network of photographers, filmmakers, and rental professionals sharing knowledge and
                  opportunities.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Marketplace Preview */}
      <section id="marketplace" className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4">Featured Equipment</h2>
            <p className="text-xl text-muted-foreground">
              Discover top-rated gear available for rent from trusted providers
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                name: "Canon EOS R5",
                category: "Mirrorless Camera",
                price: "$89/day",
                rating: 4.9,
                location: "Los Angeles, CA",
                image: "/canon-eos-r5-camera.jpg",
              },
              {
                name: "Sony FX6 Cinema Camera",
                category: "Cinema Camera",
                price: "$245/day",
                rating: 4.8,
                location: "New York, NY",
                image: "/sony-fx6-cinema-camera.jpg",
              },
              {
                name: "ARRI Alexa Mini LF",
                category: "Professional Cinema",
                price: "$890/day",
                rating: 5.0,
                location: "Atlanta, GA",
                image: "/arri-alexa-mini-lf-camera.jpg",
              },
            ].map((item, index) => (
              <Card key={index} className="overflow-hidden card-gradient hover:shadow-lg transition-all duration-300 group">
                <div className="aspect-video bg-muted relative overflow-hidden">
                  <img src={item.image || "/placeholder.svg"} alt={item.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </div>
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-lg">{item.name}</h3>
                    <Badge variant="secondary" className="glow-effect">{item.category}</Badge>
                  </div>
                  <div className="flex items-center gap-2 mb-3">
                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    <span className="text-sm font-medium">{item.rating}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                    <MapPin className="h-4 w-4" />
                    {item.location}
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-2xl font-bold gradient-text">{item.price}</span>
                    <Button size="sm" className="glow-effect">View Details</Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="text-center mt-12">
            <Button size="lg" variant="outline" asChild>
              <Link href="/explore">
                View All Equipment
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 relative overflow-hidden">
        <div className="absolute inset-0 gradient-bg" />
        <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-accent/10 to-primary/20" />
        <div className="container mx-auto px-4 text-center relative">
          <h2 className="text-3xl lg:text-4xl font-bold mb-6 gradient-text">Ready to Elevate Your Creative Projects?</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto opacity-90">
            Join thousands of visual creators who trust Altoscope for their equipment needs.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" className="text-lg px-8 glow-effect">
              Start Exploring
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="text-lg px-8 border-primary/50 text-foreground hover:bg-primary/10 bg-transparent backdrop-blur-sm"
            >
              List Your Equipment
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 py-12 bg-muted/20">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Camera className="h-6 w-6 text-primary glow-effect" />
                <span className="text-xl font-bold gradient-text">Altoscope</span>
              </div>
              <p className="text-muted-foreground">
                Empowering visual creators with the right tools for every project.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Platform</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Browse Equipment
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Rent Gear
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-foreground">
                    List Equipment
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Community</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Creator Stories
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Equipment Reviews
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Forums
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Contact Us
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Safety Guidelines
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t mt-8 pt-8 text-center text-muted-foreground">
            <p>&copy; 2024 Altoscope. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
