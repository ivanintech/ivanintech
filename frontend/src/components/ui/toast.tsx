import * as React from "react"
import { cn } from "@/lib/utils"

interface ToastProps {
  message: string
  isVisible: boolean
  onClose: () => void
  duration?: number
}

export function Toast({ message, isVisible, onClose, duration = 3000 }: ToastProps) {
  React.useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        onClose()
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [isVisible, onClose, duration])

  if (!isVisible) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 animate-in slide-in-from-bottom-2 duration-300">
      <div className={cn(
        "bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg",
        "flex items-center gap-2"
      )}>
        <span className="text-sm font-medium">{message}</span>
        <button
          onClick={onClose}
          className="text-white hover:text-gray-200 ml-2"
        >
          ×
        </button>
      </div>
    </div>
  )
}

// Hook para usar el toast
export function useToast() {
  const [toast, setToast] = React.useState<{
    message: string
    isVisible: boolean
  }>({
    message: "",
    isVisible: false
  })

  const showToast = (message: string) => {
    setToast({
      message,
      isVisible: true
    })
  }

  const hideToast = () => {
    setToast(prev => ({
      ...prev,
      isVisible: false
    }))
  }

  return {
    toast,
    showToast,
    hideToast
  }
} 