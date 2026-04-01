export default function Messaging() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Messages</h1>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        <div className="rounded-lg bg-white p-4 shadow-md lg:col-span-1">
          <p className="text-gray-600">Conversations list...</p>
        </div>
        <div className="rounded-lg bg-white p-6 shadow-md lg:col-span-3">
          <p className="text-gray-600">Chat window coming soon...</p>
        </div>
      </div>
    </div>
  )
}
