import React from 'react'
import { LightningIcon, AnalyticsIcon, LockIcon } from '../components/icons'

export interface Feature {
    icon: React.ReactNode
    title: string
    description: string
    iconBgClass: string
}

export const features: Feature[] = [
    {
        icon: <AnalyticsIcon className="w-4 h-4 text-white" />,
        title: 'Smart Analytics',
        description: 'AI-powered insights from your log data with intelligent pattern recognition',
        iconBgClass: 'bg-gradient-to-br from-blue-500 to-blue-600'
    },
    {
        icon: <LightningIcon className="w-4 h-4 text-white" />,
        title: 'Real-time Processing',
        description: 'Stream and analyze logs as they happen with zero latency',
        iconBgClass: 'bg-gradient-to-br from-purple-500 to-purple-600'
    },
    {
        icon: <LockIcon className="w-4 h-4 text-white" />,
        title: 'Secure & Scalable',
        description: 'Enterprise-grade security and performance at any scale',
        iconBgClass: 'bg-gradient-to-br from-indigo-500 to-indigo-600'
    }
]