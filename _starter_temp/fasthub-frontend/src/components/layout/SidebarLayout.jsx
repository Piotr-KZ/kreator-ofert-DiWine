export default function SidebarLayout({ tabs, activeTab, onTabChange, children }) {
  return (
    <div className="flex gap-0 -m-8 h-[calc(100%+4rem)]">
      <div className="w-56 bg-white border-r border-gray-200 p-4 overflow-auto flex-shrink-0">
        <div className="space-y-0.5">
          {tabs.map(t => (
            <button key={t.id} onClick={() => onTabChange(t.id)}
              className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-all ${activeTab === t.id ? "bg-indigo-50 text-indigo-700 font-semibold" : "text-gray-600 hover:bg-gray-50"}`}>
              {t.name}
            </button>
          ))}
        </div>
      </div>
      <div className="flex-1 overflow-auto p-8">
        <div className="max-w-3xl mx-auto">
          {children}
        </div>
      </div>
    </div>
  );
}
