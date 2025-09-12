"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Camera, Search, Filter, Star, MapPin, ArrowLeft, Heart, Share2 } from "lucide-react"
import Link from "next/link"

const equipmentData = [
  {
    id: 1,
    name: "Canon EOS R5",
    category: "Mirrorless Camera",
    brand: "Canon",
    price: 89,
    rating: 4.9,
    reviews: 127,
    location: "Los Angeles, CA",
    availability: "Available",
    specs: ["45MP Full Frame", "8K Video", "In-Body Stabilization"],
    image: "/canon-eos-r5-professional-camera.jpg",
  },
  {
    id: 2,
    name: "Sony FX6 Cinema Camera",
    category: "Cinema Camera",
    brand: "Sony",
    price: 245,
    rating: 4.8,
    reviews: 89,
    location: "New York, NY",
    availability: "Available",
    specs: ["Full Frame Sensor", "4K 120p", "Dual Base ISO"],
    image: "/sony-fx6-cinema-camera-professional.jpg",
  },
  {
    id: 3,
    name: "ARRI Alexa Mini LF",
    category: "Professional Cinema",
    brand: "ARRI",
    price: 890,
    rating: 5.0,
    reviews: 45,
    location: "Atlanta, GA",
    availability: "Booked until Dec 15",
    specs: ["Large Format Sensor", "4.5K Recording", "ARRI Color Science"],
    image: "/arri-alexa-mini-lf-cinema-camera.jpg",
  },
  {
    id: 4,
    name: "RED Komodo 6K",
    category: "Cinema Camera",
    brand: "RED",
    price: 320,
    rating: 4.7,
    reviews: 73,
    location: "Los Angeles, CA",
    availability: "Available",
    specs: ["6K Global Shutter", "Compact Design", "RF Mount"],
    image: "/red-komodo-6k-cinema-camera.jpg",
  },
  {
    id: 5,
    name: "Canon CN-E 24-70mm T2.95",
    category: "Cinema Lens",
    brand: "Canon",
    price: 125,
    rating: 4.9,
    reviews: 156,
    location: "Chicago, IL",
    availability: "Available",
    specs: ["T2.95 Constant Aperture", "Cinema Focus Ring", "EF Mount"],
    image: "/canon-cinema-lens-24-70mm-professional.jpg",
  },
  {
    id: 6,
    name: "ARRI SkyPanel S60-C",
    category: "LED Light",
    brand: "ARRI",
    price: 180,
    rating: 4.8,
    reviews: 92,
    location: "Miami, FL",
    availability: "Available",
    specs: ["Full Color LED", "Wireless Control", "High CRI"],
    image: "/arri-skypanel-led-light-professional.jpg",
  },
]

export default function ExplorePage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [priceRange, setPriceRange] = useState([0, 1000])
  const [filteredEquipment, setFilteredEquipment] = useState(equipmentData)

  const categories = ["all", "Mirrorless Camera", "Cinema Camera", "Professional Cinema", "Cinema Lens", "LED Light"]

  const handleSearch = () => {
    let filtered = equipmentData

    if (searchTerm) {
      filtered = filtered.filter(
        (item) =>
          item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.brand.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.category.toLowerCase().includes(searchTerm.toLowerCase()),
      )
    }

    if (selectedCategory !== "all") {
      filtered = filtered.filter((item) => item.category === selectedCategory)
    }

    filtered = filtered.filter((item) => item.price >= priceRange[0] && item.price <= priceRange[1])

    setFilteredEquipment(filtered)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" asChild>
              <Link href="/">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Link>
            </Button>
            <div className="flex items-center space-x-2">
              <Camera className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold text-foreground">Altoscope</span>
            </div>
          </div>
          <nav className="hidden md:flex items-center space-x-6">
            <Button variant="outline" size="sm">
              Sign In
            </Button>
            <Button size="sm">Get Started</Button>
          </nav>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Explore Equipment</h1>
          <p className="text-muted-foreground">Discover professional camera equipment from trusted rental providers</p>
        </div>

        <div className="grid lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Filter className="h-5 w-5" />
                  Filters
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Search */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Search</label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                    <Input
                      placeholder="Search equipment..."
                      className="pl-10"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>

                {/* Category */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Category</label>
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category} value={category}>
                          {category === "all" ? "All Categories" : category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Price Range */}
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Price Range: ${priceRange[0]} - ${priceRange[1]}/day
                  </label>
                  <Slider value={priceRange} onValueChange={setPriceRange} max={1000} step={10} className="mt-2" />
                </div>

                <Button onClick={handleSearch} className="w-full">
                  Apply Filters
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Equipment Grid */}
          <div className="lg:col-span-3">
            <div className="flex justify-between items-center mb-6">
              <p className="text-muted-foreground">Showing {filteredEquipment.length} results</p>
              <Select defaultValue="rating">
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="rating">Sort by Rating</SelectItem>
                  <SelectItem value="price-low">Price: Low to High</SelectItem>
                  <SelectItem value="price-high">Price: High to Low</SelectItem>
                  <SelectItem value="newest">Newest First</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
              {filteredEquipment.map((item) => (
                <Card key={item.id} className="overflow-hidden hover:shadow-lg transition-all duration-300 group">
                  <div className="relative aspect-video bg-muted">
                    <img
                      src={item.image || "/placeholder.svg"}
                      alt={item.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-3 right-3 flex gap-2">
                      <Button size="sm" variant="secondary" className="h-8 w-8 p-0">
                        <Heart className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="secondary" className="h-8 w-8 p-0">
                        <Share2 className="h-4 w-4" />
                      </Button>
                    </div>
                    <Badge
                      variant={item.availability === "Available" ? "default" : "secondary"}
                      className="absolute bottom-3 left-3"
                    >
                      {item.availability}
                    </Badge>
                  </div>

                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
                          {item.name}
                        </h3>
                        <p className="text-sm text-muted-foreground">{item.brand}</p>
                      </div>
                      <Badge variant="outline">{item.category}</Badge>
                    </div>

                    <div className="flex items-center gap-2 mb-3">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span className="text-sm font-medium">{item.rating}</span>
                      <span className="text-sm text-muted-foreground">({item.reviews} reviews)</span>
                    </div>

                    <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                      <MapPin className="h-4 w-4" />
                      {item.location}
                    </div>

                    <div className="space-y-2 mb-4">
                      {item.specs.map((spec, index) => (
                        <Badge key={index} variant="secondary" className="text-xs mr-1">
                          {spec}
                        </Badge>
                      ))}
                    </div>

                    <div className="flex justify-between items-center">
                      <div>
                        <span className="text-2xl font-bold text-primary">${item.price}</span>
                        <span className="text-muted-foreground">/day</span>
                      </div>
                      <Button size="sm" disabled={item.availability !== "Available"}>
                        {item.availability === "Available" ? "Book Now" : "Unavailable"}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {filteredEquipment.length === 0 && (
              <div className="text-center py-12">
                <Camera className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">No equipment found</h3>
                <p className="text-muted-foreground">Try adjusting your filters or search terms</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
