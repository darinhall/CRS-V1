import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Camera, ArrowLeft, Star, CheckCircle, XCircle, Zap, Battery, Wifi, Video } from "lucide-react"
import Link from "next/link"

export default function CanonComparePage() {
  const cameras = [
    {
      name: "Canon EOS R5",
      price: "$3,899",
      image: "/canon-eos-r5-camera.jpg",
      specs: {
        resolution: "45MP",
        video: "8K RAW",
        stabilization: "5-axis IBIS",
        autofocus: "Dual Pixel AF II",
        battery: "LP-E6NH",
        connectivity: "Wi-Fi, Bluetooth",
        weight: "650g"
      },
      pros: [
        "8K video recording",
        "Excellent image quality",
        "Fast autofocus",
        "Great stabilization"
      ],
      cons: [
        "Expensive",
        "Heavy",
        "Limited battery life"
      ],
      rating: 4.8
    },
    {
      name: "Canon EOS R6 Mark II",
      price: "$2,499",
      image: "/canon-eos-r5-professional-camera.jpg",
      specs: {
        resolution: "24MP",
        video: "4K 60p",
        stabilization: "5-axis IBIS",
        autofocus: "Dual Pixel AF II",
        battery: "LP-E6NH",
        connectivity: "Wi-Fi, Bluetooth",
        weight: "588g"
      },
      pros: [
        "Great value",
        "Fast burst shooting",
        "Good low light performance",
        "Reliable autofocus"
      ],
      cons: [
        "Lower resolution",
        "No 8K video",
        "Smaller buffer"
      ],
      rating: 4.6
    }
  ]

  return (
    <div className="min-h-screen bg-background dark">
      {/* Header */}
      <header className="border-b border-border/50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
              <ArrowLeft className="h-5 w-5 text-primary" />
              <span className="text-sm text-muted-foreground">Back to Home</span>
            </Link>
            <div className="h-6 w-px bg-border" />
            <div className="flex items-center space-x-2">
              <Camera className="h-8 w-8 text-primary" />
              <span className="text-2xl font-bold text-foreground">Canon Camera Comparison</span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 lg:py-32 overflow-hidden">
        <div className="absolute inset-0 gradient-bg" />
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-accent/5 to-primary/10" />
        <div className="container mx-auto px-4 relative">
          <div className="max-w-4xl mx-auto text-center">
            <Badge variant="secondary" className="mb-6 glow-effect">
              Professional Camera Comparison
            </Badge>
            <h1 className="text-4xl lg:text-6xl font-bold text-balance mb-6">
              Canon <span className="gradient-text">EOS R Series</span> Comparison
            </h1>
            <p className="text-xl text-muted-foreground text-balance mb-8 max-w-2xl mx-auto">
              Compare the latest Canon mirrorless cameras side by side. Find the perfect camera for your creative needs.
            </p>
          </div>
        </div>
      </section>

      {/* Comparison Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="grid lg:grid-cols-2 gap-8">
            {cameras.map((camera, index) => (
              <Card key={index} className="card-gradient float-animation" style={{ animationDelay: `${index * 0.3}s` }}>
                <CardHeader className="text-center">
                  <div className="aspect-video bg-muted rounded-lg mb-6 overflow-hidden">
                    <img 
                      src={camera.image} 
                      alt={camera.name} 
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" 
                    />
                  </div>
                  <CardTitle className="text-2xl gradient-text">{camera.name}</CardTitle>
                  <CardDescription className="text-lg font-semibold text-primary">
                    {camera.price}
                  </CardDescription>
                  <div className="flex items-center justify-center gap-2">
                    <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                    <span className="text-lg font-medium">{camera.rating}</span>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-6">
                  {/* Specifications */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <Zap className="h-5 w-5 text-primary" />
                      Specifications
                    </h3>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Resolution:</span>
                        <span className="font-medium">{camera.specs.resolution}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Video:</span>
                        <span className="font-medium">{camera.specs.video}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Stabilization:</span>
                        <span className="font-medium">{camera.specs.stabilization}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Autofocus:</span>
                        <span className="font-medium">{camera.specs.autofocus}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Battery:</span>
                        <span className="font-medium">{camera.specs.battery}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Weight:</span>
                        <span className="font-medium">{camera.specs.weight}</span>
                      </div>
                    </div>
                  </div>

                  {/* Pros */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      Pros
                    </h3>
                    <ul className="space-y-2">
                      {camera.pros.map((pro, proIndex) => (
                        <li key={proIndex} className="flex items-start gap-2 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          <span>{pro}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Cons */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <XCircle className="h-5 w-5 text-red-500" />
                      Cons
                    </h3>
                    <ul className="space-y-2">
                      {camera.cons.map((con, conIndex) => (
                        <li key={conIndex} className="flex items-start gap-2 text-sm">
                          <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                          <span>{con}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-3 pt-4">
                    <Button className="flex-1 glow-effect">
                      View Details
                    </Button>
                    <Button variant="outline" className="flex-1">
                      Compare
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Summary */}
          <Card className="mt-12 card-gradient">
            <CardHeader>
              <CardTitle className="text-2xl text-center gradient-text">Quick Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-semibold mb-4 text-primary">Choose EOS R5 if you need:</h3>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Highest resolution (45MP)</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>8K video recording</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Professional photography</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-4 text-accent">Choose EOS R6 Mark II if you need:</h3>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Better value for money</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Faster burst shooting</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Lighter weight</span>
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  )
}