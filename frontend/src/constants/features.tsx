import React from 'react'

export interface Feature {
    icon: React.ReactNode
    title: string
    description: string
    iconBgClass: string
}

export const features: Feature[] = [
    {
        icon: (
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
        ),
        title: 'Smart Analytics',
        description: 'AI-powered insights from your log data with intelligent pattern recognition',
        iconBgClass: 'bg-gradient-to-br from-blue-500 to-blue-600'
    },
    {
        icon: (
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
        ),
        title: 'Real-time Processing',
        description: 'Stream and analyze logs as they happen with zero latency',
        iconBgClass: 'bg-gradient-to-br from-purple-500 to-purple-600'
    },
    {
        icon: (
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
        ),
        title: 'Secure & Scalable',
        description: 'Enterprise-grade security and performance at any scale',
        iconBgClass: 'bg-gradient-to-br from-indigo-500 to-indigo-600'
    }
]