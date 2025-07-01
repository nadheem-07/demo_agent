"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Building2, X } from "lucide-react";

interface BusinessFormProps {
  onSubmit: (businessData: BusinessFormData) => void;
  onCancel: () => void;
}

export interface BusinessFormData {
  companyName: string;
  industrySector: string;
  subSector: string;
  location: string;
  positionTitle: string;
  legalStructure: string;
  establishmentYear: string;
  productsOrServices: string;
  briefDescription: string;
  web?: string;
}

export function BusinessForm({ onSubmit, onCancel }: BusinessFormProps) {
  const [formData, setFormData] = useState<BusinessFormData>({
    companyName: "",
    industrySector: "",
    subSector: "",
    location: "",
    positionTitle: "",
    legalStructure: "",
    establishmentYear: "",
    productsOrServices: "",
    briefDescription: "",
    web: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleInputChange = (field: keyof BusinessFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: "" }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.companyName.trim()) newErrors.companyName = "Company name is required";
    if (!formData.industrySector.trim()) newErrors.industrySector = "Industry sector is required";
    if (!formData.subSector.trim()) newErrors.subSector = "Sub-sector is required";
    if (!formData.location.trim()) newErrors.location = "Location is required";
    if (!formData.positionTitle.trim()) newErrors.positionTitle = "Position title is required";
    if (!formData.legalStructure.trim()) newErrors.legalStructure = "Legal structure is required";
    if (!formData.establishmentYear.trim()) newErrors.establishmentYear = "Establishment year is required";
    if (!formData.productsOrServices.trim()) newErrors.productsOrServices = "Products/Services is required";
    if (!formData.briefDescription.trim()) newErrors.briefDescription = "Brief description is required";

    // Validate establishment year
    if (formData.establishmentYear && !/^\d{4}$/.test(formData.establishmentYear)) {
      newErrors.establishmentYear = "Please enter a valid 4-digit year";
    }

    // Validate website URL if provided
    if (formData.web && formData.web.trim() && !formData.web.startsWith("http")) {
      setFormData(prev => ({ ...prev, web: `https://${prev.web}` }));
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const industryOptions = [
    "Technology", "Healthcare", "Finance", "Manufacturing", "Retail", "Education",
    "Real Estate", "Hospitality", "Transportation", "Energy", "Agriculture",
    "Media & Entertainment", "Consulting", "Legal Services", "Other"
  ];

  const legalStructureOptions = [
    "Private Limited Company", "Public Limited Company", "Partnership",
    "Sole Proprietorship", "LLP", "NGO", "Government", "Other"
  ];

  return (
    <Card className="w-full max-w-2xl mx-auto my-4 bg-white shadow-lg">
      <CardHeader className="bg-blue-50 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Building2 className="h-6 w-6 text-blue-600" />
            <CardTitle className="text-xl text-blue-800">Register Your Business</CardTitle>
          </div>
          <Button variant="ghost" size="sm" onClick={onCancel}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Company Name */}
            <div className="md:col-span-2">
              <Label htmlFor="companyName" className="text-sm font-medium">
                Company Name *
              </Label>
              <Input
                id="companyName"
                value={formData.companyName}
                onChange={(e) => handleInputChange("companyName", e.target.value)}
                placeholder="e.g., Medway Hospitals"
                className={errors.companyName ? "border-red-500" : ""}
              />
              {errors.companyName && <p className="text-red-500 text-xs mt-1">{errors.companyName}</p>}
            </div>

            {/* Industry Sector */}
            <div>
              <Label htmlFor="industrySector" className="text-sm font-medium">
                Industry Sector *
              </Label>
              <select
                id="industrySector"
                value={formData.industrySector}
                onChange={(e) => handleInputChange("industrySector", e.target.value)}
                className={`w-full h-10 px-3 py-2 border rounded-md bg-background text-sm ${
                  errors.industrySector ? "border-red-500" : "border-input"
                }`}
              >
                <option value="">Select Industry</option>
                {industryOptions.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
              {errors.industrySector && <p className="text-red-500 text-xs mt-1">{errors.industrySector}</p>}
            </div>

            {/* Sub Sector */}
            <div>
              <Label htmlFor="subSector" className="text-sm font-medium">
                Sub-Sector *
              </Label>
              <Input
                id="subSector"
                value={formData.subSector}
                onChange={(e) => handleInputChange("subSector", e.target.value)}
                placeholder="e.g., Hospitals"
                className={errors.subSector ? "border-red-500" : ""}
              />
              {errors.subSector && <p className="text-red-500 text-xs mt-1">{errors.subSector}</p>}
            </div>

            {/* Location */}
            <div>
              <Label htmlFor="location" className="text-sm font-medium">
                Location *
              </Label>
              <Input
                id="location"
                value={formData.location}
                onChange={(e) => handleInputChange("location", e.target.value)}
                placeholder="e.g., Tamil Nadu and Seemandhra"
                className={errors.location ? "border-red-500" : ""}
              />
              {errors.location && <p className="text-red-500 text-xs mt-1">{errors.location}</p>}
            </div>

            {/* Position Title */}
            <div>
              <Label htmlFor="positionTitle" className="text-sm font-medium">
                Your Position *
              </Label>
              <Input
                id="positionTitle"
                value={formData.positionTitle}
                onChange={(e) => handleInputChange("positionTitle", e.target.value)}
                placeholder="e.g., Chairman"
                className={errors.positionTitle ? "border-red-500" : ""}
              />
              {errors.positionTitle && <p className="text-red-500 text-xs mt-1">{errors.positionTitle}</p>}
            </div>

            {/* Legal Structure */}
            <div>
              <Label htmlFor="legalStructure" className="text-sm font-medium">
                Legal Structure *
              </Label>
              <select
                id="legalStructure"
                value={formData.legalStructure}
                onChange={(e) => handleInputChange("legalStructure", e.target.value)}
                className={`w-full h-10 px-3 py-2 border rounded-md bg-background text-sm ${
                  errors.legalStructure ? "border-red-500" : "border-input"
                }`}
              >
                <option value="">Select Legal Structure</option>
                {legalStructureOptions.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
              {errors.legalStructure && <p className="text-red-500 text-xs mt-1">{errors.legalStructure}</p>}
            </div>

            {/* Establishment Year */}
            <div>
              <Label htmlFor="establishmentYear" className="text-sm font-medium">
                Establishment Year *
              </Label>
              <Input
                id="establishmentYear"
                value={formData.establishmentYear}
                onChange={(e) => handleInputChange("establishmentYear", e.target.value)}
                placeholder="e.g., 2020"
                maxLength={4}
                className={errors.establishmentYear ? "border-red-500" : ""}
              />
              {errors.establishmentYear && <p className="text-red-500 text-xs mt-1">{errors.establishmentYear}</p>}
            </div>

            {/* Website */}
            <div>
              <Label htmlFor="web" className="text-sm font-medium">
                Website (Optional)
              </Label>
              <Input
                id="web"
                value={formData.web}
                onChange={(e) => handleInputChange("web", e.target.value)}
                placeholder="e.g., www.medwayhospitals.com"
              />
            </div>

            {/* Products/Services */}
            <div className="md:col-span-2">
              <Label htmlFor="productsOrServices" className="text-sm font-medium">
                Products/Services *
              </Label>
              <Input
                id="productsOrServices"
                value={formData.productsOrServices}
                onChange={(e) => handleInputChange("productsOrServices", e.target.value)}
                placeholder="e.g., Healthcare"
                className={errors.productsOrServices ? "border-red-500" : ""}
              />
              {errors.productsOrServices && <p className="text-red-500 text-xs mt-1">{errors.productsOrServices}</p>}
            </div>

            {/* Brief Description */}
            <div className="md:col-span-2">
              <Label htmlFor="briefDescription" className="text-sm font-medium">
                Brief Description *
              </Label>
              <Textarea
                id="briefDescription"
                value={formData.briefDescription}
                onChange={(e) => handleInputChange("briefDescription", e.target.value)}
                placeholder="e.g., Chain of super speciality hospitals"
                rows={3}
                className={errors.briefDescription ? "border-red-500" : ""}
              />
              {errors.briefDescription && <p className="text-red-500 text-xs mt-1">{errors.briefDescription}</p>}
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Button type="submit" className="flex-1 bg-blue-600 hover:bg-blue-700">
              Register Business
            </Button>
            <Button type="button" variant="outline" onClick={onCancel} className="flex-1">
              Cancel
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}