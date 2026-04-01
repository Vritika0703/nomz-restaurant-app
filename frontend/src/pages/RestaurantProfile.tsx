import { useParams } from 'react-router-dom'

export default function RestaurantProfile() {
  const { id } = useParams()

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Restaurant Profile</h1>
      <div className="rounded-lg bg-white p-6 shadow-md">
        <p className="text-gray-600">Restaurant #{id} details coming soon...</p>
      </div>
    </div>
  )
}
