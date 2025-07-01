// "use client";

// import { useState } from "react";
// import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
// import { Button } from "@/components/ui/button";
// import { Input } from "@/components/ui/input";
// import { Label } from "@/components/ui/label";
// import { User, CalendarCheck, QrCode } from "lucide-react";

// interface CustomerLoginProps {
//   onLogin: (identifier: string, userInfo: any) => void;
// }

// export function CustomerLogin({ onLogin }: CustomerLoginProps) {
//   const [identifier, setIdentifier] = useState("");
//   const [loginType, setLoginType] = useState<"registration" | "qr">("registration");
//   const [isLoading, setIsLoading] = useState(false);
//   const [error, setError] = useState("");

//   const handleLogin = async () => {
//     if (!identifier.trim()) {
//       setError(`Please enter your ${loginType === "registration" ? "registration ID" : "QR code"}`);
//       return;
//     }

//     setIsLoading(true);
//     setError("");

//     try {
//       // Use the new user endpoint that handles both registration_id and QR code
//       const response = await fetch(`http://localhost:8000/user/${identifier}`, {
//         method: "GET",
//         headers: {
//           "Content-Type": "application/json",
//         },
//       });
      
//       if (!response.ok) {
//         if (response.status === 404) {
//           setError(`${loginType === "registration" ? "Registration ID" : "QR code"} not found. Please check and try again.`);
//         } else {
//           setError("Failed to load user information. Please try again.");
//         }
//         return;
//       }

//       const userData = await response.json();
      
//       // Validate user data
//       if (!userData || !userData.name || !userData.account_number) {
//         setError("Invalid user data received. Please try again.");
//         return;
//       }

//       onLogin(identifier, userData);
//     } catch (err) {
//       setError("Network error. Please check your connection and try again.");
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleKeyPress = (e: React.KeyboardEvent) => {
//     if (e.key === "Enter") {
//       handleLogin();
//     }
//   };

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
//       <Card className="w-full max-w-md shadow-xl border-0">
//         <CardHeader className="text-center pb-2">
//           <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
//             <CalendarCheck className="h-8 w-8 text-white" />
//           </div>
//           <CardTitle className="text-2xl font-bold text-gray-900">
//             Business Conference 2025
//           </CardTitle>
//           <p className="text-gray-600 text-sm">
//             Enter your registration ID or scan QR code to access conference information
//           </p>
//         </CardHeader>
//         <CardContent className="space-y-4">
//           {/* Login Type Selector */}
//           <div className="flex space-x-2 mb-4">
//             <Button
//               type="button"
//               variant={loginType === "registration" ? "default" : "outline"}
//               onClick={() => {
//                 setLoginType("registration");
//                 setIdentifier("");
//                 setError("");
//               }}
//               className="flex-1 h-10"
//             >
//               <User className="h-4 w-4 mr-2" />
//               Registration ID
//             </Button>
//             <Button
//               type="button"
//               variant={loginType === "qr" ? "default" : "outline"}
//               onClick={() => {
//                 setLoginType("qr");
//                 setIdentifier("");
//                 setError("");
//               }}
//               className="flex-1 h-10"
//             >
//               <QrCode className="h-4 w-4 mr-2" />
//               QR Code
//             </Button>
//           </div>

//           <div className="space-y-2">
//             <Label htmlFor="identifier" className="text-sm font-medium text-gray-700">
//               {loginType === "registration" ? "Registration ID" : "QR Code"}
//             </Label>
//             <div className="relative">
//               {loginType === "registration" ? (
//                 <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
//               ) : (
//                 <QrCode className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
//               )}
//               <Input
//                 id="identifier"
//                 type="text"
//                 placeholder={
//                   loginType === "registration" 
//                     ? "e.g., 50464" 
//                     : "e.g., 0c671788-28a8-48e0-8f6f-4d099f0fbd46"
//                 }
//                 value={identifier}
//                 onChange={(e) => setIdentifier(e.target.value)}
//                 onKeyPress={handleKeyPress}
//                 className="pl-10 h-12 text-center font-mono tracking-wider"
//                 disabled={isLoading}
//               />
//             </div>
//           </div>

//           {error && (
//             <div className="text-red-600 text-sm text-center bg-red-50 p-3 rounded-md border border-red-200">
//               {error}
//             </div>
//           )}

//           <Button
//             onClick={handleLogin}
//             disabled={isLoading || !identifier.trim()}
//             className="w-full h-12 bg-blue-600 hover:bg-blue-700 text-white font-medium"
//           >
//             {isLoading ? "Loading..." : "Access Conference Info"}
//           </Button>

//           <div className="text-center text-xs text-gray-500 mt-4">
//             <p>Demo {loginType === "registration" ? "Registration IDs" : "QR Codes"}:</p>
//             <div className="flex justify-center gap-2 mt-1 flex-wrap">
//               {loginType === "registration" ? (
//                 <>
//                   <code className="bg-gray-100 px-2 py-1 rounded text-xs">50464</code>
//                   <code className="bg-gray-100 px-2 py-1 rounded text-xs">50465</code>
//                   <code className="bg-gray-100 px-2 py-1 rounded text-xs">50466</code>
//                 </>
//               ) : (
//                 <>
//                   <code className="bg-gray-100 px-2 py-1 rounded text-xs text-[10px]">0c671788-28a8-48e0-8f6f-4d099f0fbd46</code>
//                   <code className="bg-gray-100 px-2 py-1 rounded text-xs text-[10px]">1d782899-39b9-59f1-9g7g-5e1aacb1fc57</code>
//                 </>
//               )}
//             </div>
//           </div>
//         </CardContent>
//       </Card>
//     </div>
//   );
// }























"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { User, CalendarCheck, QrCode, Camera } from "lucide-react";

interface CustomerLoginProps {
  onLogin: (identifier: string, userInfo: any) => void;
}

export function CustomerLogin({ onLogin }: CustomerLoginProps) {
  const [identifier, setIdentifier] = useState("");
  const [loginType, setLoginType] = useState<"registration" | "qr">("registration");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isScanning, setIsScanning] = useState(false);

  const handleLogin = async () => {
    if (!identifier.trim()) {
      setError(`Please enter your ${loginType === "registration" ? "registration ID" : "QR code"}`);
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      // Use the new user endpoint that handles both registration_id and QR code
      const response = await fetch(`http://localhost:8000/user/${identifier}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
      
      if (!response.ok) {
        if (response.status === 404) {
          setError(`${loginType === "registration" ? "Registration ID" : "QR code"} not found. Please check and try again.`);
        } else {
          setError("Failed to load user information. Please try again.");
        }
        return;
      }

      const userData = await response.json();
      
      // Validate user data
      if (!userData || !userData.name || !userData.account_number) {
        setError("Invalid user data received. Please try again.");
        return;
      }

      onLogin(identifier, userData);
    } catch (err) {
      setError("Network error. Please check your connection and try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleQRScan = () => {
    setIsScanning(true);
    
    // Simulate QR code scanning - in a real app, you'd use a camera library
    // For demo purposes, we'll show a modal or use a predefined QR code
    const demoQRCodes = [
      "0c671788-28a8-48e0-8f6f-4d099f0fbd46",
      "1d782899-39b9-59f1-9g7g-5e1aacb1fc57",
      "2e893aaa-4ac0-6af2-ah8h-6f2bbdcb2gd68"
    ];
    
    // Simulate scanning delay
    setTimeout(() => {
      const randomQR = demoQRCodes[Math.floor(Math.random() * demoQRCodes.length)];
      setIdentifier(randomQR);
      setIsScanning(false);
      setError("");
    }, 2000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleLogin();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-xl border-0">
        <CardHeader className="text-center pb-2">
          <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
            <CalendarCheck className="h-8 w-8 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">
            Business Conference 2025
          </CardTitle>
          <p className="text-gray-600 text-sm">
            Enter your registration ID or scan QR code to access conference information
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Login Type Selector */}
          <div className="flex space-x-2 mb-4">
            <Button
              type="button"
              variant={loginType === "registration" ? "default" : "outline"}
              onClick={() => {
                setLoginType("registration");
                setIdentifier("");
                setError("");
              }}
              className="flex-1 h-10"
            >
              <User className="h-4 w-4 mr-2" />
              Registration ID
            </Button>
            <Button
              type="button"
              variant={loginType === "qr" ? "default" : "outline"}
              onClick={() => {
                setLoginType("qr");
                setIdentifier("");
                setError("");
              }}
              className="flex-1 h-10"
            >
              <QrCode className="h-4 w-4 mr-2" />
              QR Code
            </Button>
          </div>

          <div className="space-y-2">
            <Label htmlFor="identifier" className="text-sm font-medium text-gray-700">
              {loginType === "registration" ? "Registration ID" : "QR Code"}
            </Label>
            <div className="relative">
              {loginType === "registration" ? (
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              ) : (
                <QrCode className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              )}
              <Input
                id="identifier"
                type="text"
                placeholder={
                  loginType === "registration" 
                    ? "e.g., 50464" 
                    : "e.g., 0c671788-28a8-48e0-8f6f-4d099f0fbd46"
                }
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                onKeyPress={handleKeyPress}
                className="pl-10 h-12 text-center font-mono tracking-wider"
                disabled={isLoading || isScanning}
              />
            </div>
          </div>

          {/* QR Scanner Button */}
          {loginType === "qr" && (
            <Button
              onClick={handleQRScan}
              disabled={isLoading || isScanning}
              variant="outline"
              className="w-full h-12 border-2 border-dashed border-blue-300 hover:border-blue-500"
            >
              <Camera className="h-5 w-5 mr-2" />
              {isScanning ? "Scanning QR Code..." : "Scan QR Code"}
            </Button>
          )}

          {error && (
            <div className="text-red-600 text-sm text-center bg-red-50 p-3 rounded-md border border-red-200">
              {error}
            </div>
          )}

          <Button
            onClick={handleLogin}
            disabled={isLoading || !identifier.trim() || isScanning}
            className="w-full h-12 bg-blue-600 hover:bg-blue-700 text-white font-medium"
          >
            {isLoading ? "Loading..." : "Access Conference Info"}
          </Button>

          <div className="text-center text-xs text-gray-500 mt-4">
            <p>Demo {loginType === "registration" ? "Registration IDs" : "QR Codes"}:</p>
            <div className="flex justify-center gap-2 mt-1 flex-wrap">
              {loginType === "registration" ? (
                <>
                  <code className="bg-gray-100 px-2 py-1 rounded text-xs cursor-pointer hover:bg-gray-200" 
                        onClick={() => setIdentifier("50464")}>50464</code>
                  <code className="bg-gray-100 px-2 py-1 rounded text-xs cursor-pointer hover:bg-gray-200"
                        onClick={() => setIdentifier("50465")}>50465</code>
                  <code className="bg-gray-100 px-2 py-1 rounded text-xs cursor-pointer hover:bg-gray-200"
                        onClick={() => setIdentifier("50466")}>50466</code>
                </>
              ) : (
                <>
                  <code className="bg-gray-100 px-2 py-1 rounded text-xs text-[10px] cursor-pointer hover:bg-gray-200 break-all"
                        onClick={() => setIdentifier("0c671788-28a8-48e0-8f6f-4d099f0fbd46")}>
                    0c671788-28a8-48e0-8f6f-4d099f0fbd46
                  </code>
                  <code className="bg-gray-100 px-2 py-1 rounded text-xs text-[10px] cursor-pointer hover:bg-gray-200 break-all"
                        onClick={() => setIdentifier("1d782899-39b9-59f1-9g7g-5e1aacb1fc57")}>
                    1d782899-39b9-59f1-9g7g-5e1aacb1fc57
                  </code>
                </>
              )}
            </div>
            <p className="mt-2 text-[10px] text-gray-400">Click on demo codes to auto-fill</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}