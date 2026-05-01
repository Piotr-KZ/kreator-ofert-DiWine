import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = '/api/v1/offers';
type Tab = 'wines'|'sweets'|'personalization'|'deco'|'packaging'|'discounts'|'stock'|'suppliers'|'company'|'graphics'|'client_logos'|'photos';
const TABS: {id:Tab;label:string}[] = [
  {id:'wines',label:'Wina'},{id:'sweets',label:'Słodycze'},{id:'personalization',label:'Personalizacja'},
  {id:'deco',label:'Dodatki'},{id:'packaging',label:'Opakowania'},{id:'discounts',label:'Rabaty'},
  {id:'stock',label:'Stany'},{id:'suppliers',label:'Dostawcy'},{id:'company',label:'Dane DiWine'},
  {id:'graphics',label:'Grafiki'},{id:'client_logos',label:'Logo klientów'},{id:'photos',label:'Zdjęcia'},
];
const WC:Record<string,string>={czerwone:'#DC2626',białe:'#FEF9E7',różowe:'#FBCFE8',pomarańczowe:'#EA580C'};
const SC:Record<string,string>={red:'#DC2626',gold:'#D97706',green:'#16A34A',blue:'#2563EB',yellow:'#EAB308',craft:'#8B5E3C',pastel:'#F9A8D4',silver:'#9CA3AF'};
const COLOR_NAMES:Record<string,string>={red:'czerwone',gold:'złote',green:'zielone',blue:'niebieskie',yellow:'żółte',craft:'kraft',pastel:'pastelowe',silver:'srebrne'};
const INP='w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400 bg-white';
const LBL='text-[10px] text-gray-400 block mb-0.5';

/* ─── Helpers ─── */
function Modal({title,onClose,children}:{title:string;onClose:()=>void;children:React.ReactNode}){
  return(<div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" onClick={onClose}>
    <div className="bg-white rounded-xl max-w-lg w-full shadow-xl max-h-[90vh] overflow-y-auto" onClick={e=>e.stopPropagation()}>
      <div className="flex items-center justify-between p-5 border-b"><h3 className="font-bold text-gray-900">{title}</h3><button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">&times;</button></div>
      <div className="p-5">{children}</div>
    </div>
  </div>);
}
function ConfirmDialog({msg,onYes,onNo}:{msg:string;onYes:()=>void;onNo:()=>void}){
  return(<div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center"><div className="bg-white rounded-xl p-6 max-w-sm w-full mx-4 shadow-xl">
    <p className="text-sm text-gray-700 mb-5">{msg}</p><div className="flex gap-3 justify-end">
      <button onClick={onNo} className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">Anuluj</button>
      <button onClick={onYes} className="px-4 py-2 text-sm font-bold bg-red-600 text-white rounded-lg hover:bg-red-700">Usuń</button>
    </div></div></div>);
}
function TabHeader({title,count,onAdd}:{title:string;count:number;onAdd?:()=>void}){
  return(<div className="flex items-center justify-between mb-4"><h2 className="text-lg font-bold text-gray-900">{title} ({count})</h2>
    {onAdd&&<button onClick={onAdd} className="px-4 py-2 text-sm font-bold bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">+ Dodaj</button>}</div>);
}
function ActionBtns({onEdit,onDelete}:{onEdit:()=>void;onDelete:()=>void}){
  return(<div className="flex gap-1 justify-end">
    <button onClick={onEdit} className="px-3 py-1 text-xs font-medium text-indigo-600 hover:bg-indigo-50 rounded-lg">Edytuj</button>
    <button onClick={onDelete} className="px-3 py-1 text-xs font-medium text-red-500 hover:bg-red-50 rounded-lg">Kasuj</button>
  </div>);
}
function UploadBtn({label,endpoint,onDone}:{label:string;endpoint:string;onDone:()=>void}){
  const ref=useRef<HTMLInputElement>(null);const [up,setUp]=useState(false);
  return(<><input ref={ref} type="file" accept="image/*" onChange={async e=>{const f=e.target.files?.[0];if(!f)return;setUp(true);try{const fd=new FormData();fd.append('file',f);await axios.post(endpoint,fd,{headers:{'Content-Type':'multipart/form-data'}});onDone();}catch{alert('Błąd uploadu');}finally{setUp(false);if(ref.current)ref.current.value='';}}} className="hidden"/>
    <button onClick={()=>ref.current?.click()} disabled={up} className={`px-4 py-2 text-sm font-bold rounded-lg ${up?'bg-gray-300 text-gray-500':'bg-indigo-600 text-white hover:bg-indigo-700'}`}>{up?'Wgrywam...':label}</button></>);
}

export default function OfferSettings(){
  const nav=useNavigate();const [tab,setTab]=useState<Tab>('wines');
  const [prods,setProds]=useState<any[]>([]);const [pkgs,setPkgs]=useState<any[]>([]);
  const [discs,setDiscs]=useState<any[]>([]);const [photos,setPhotos]=useState<any[]>([]);
  const [clients,setClients]=useState<any[]>([]);const [sups,setSups]=useState<any[]>([]);
  const [co,setCo]=useState<any>({});const [saving,setSaving]=useState(false);
  const [photoTab,setPhotoTab]=useState<'unsplash'|'diwine'|'inne'>('unsplash');
  const [loading,setLoading]=useState(true);
  const [modal,setModal]=useState<{type:string;item:any}|null>(null);
  const [confirm,setConfirm]=useState<{msg:string;onYes:()=>void}|null>(null);
  const [openStock,setOpenStock]=useState<string[]>(['wines']);

  const reload=()=>{Promise.all([
    axios.get(`${API}/catalog/products`),axios.get(`${API}/catalog/packagings`),
    axios.get(`${API}/catalog/discounts`),axios.get(`${API}/photos/library?limit=200`).catch(()=>({data:[]})),
    axios.get(`${API}/clients`).catch(()=>({data:[]})),axios.get(`${API}/catalog/suppliers`).catch(()=>({data:[]})),
    axios.get(`${API}/company-settings`).catch(()=>({data:{}})),
  ]).then(([p,pk,d,ph,cl,su,cs])=>{
    setProds(p.data);setPkgs(pk.data);setDiscs(d.data);setPhotos(ph.data);setClients(cl.data);setSups(su.data);setCo(cs.data);
  }).finally(()=>setLoading(false));};

  useEffect(()=>{setLoading(true);reload();},[]);
  const wines=prods.filter(p=>p.category==='wine');
  const sweets=prods.filter(p=>p.category==='sweet');
  const decos=prods.filter(p=>p.category==='decoration');
  const pers=prods.filter(p=>p.category==='personalization');

  // Expand color rows for sweets/decos
  const expandColors=(items:any[])=>items.flatMap(s=>
    (s.available_colors_json&&s.available_colors_json.length>0)
      ?s.available_colors_json.map((c:string)=>({...s,_color:c,_name:`${s.name} — ${COLOR_NAMES[c]||c}`}))
      :[{...s,_color:null,_name:s.name}]
  );

  // API helpers
  const deleteProduct=async(id:string)=>{try{await axios.delete(`${API}/catalog/products/${id}`);}catch(e:any){alert(e.response?.data?.detail||'Błąd');}setConfirm(null);reload();};
  const deletePackaging=async(id:string)=>{try{await axios.delete(`${API}/catalog/packagings/${id}`);}catch(e:any){alert(e.response?.data?.detail||'Błąd');}setConfirm(null);reload();};
  const deleteSupplier=async(id:string)=>{try{await axios.delete(`${API}/catalog/suppliers/${id}`);}catch(e:any){alert(e.response?.data?.detail||'Błąd');setConfirm(null);return;}setConfirm(null);reload();};
  const deleteDiscount=async(id:string)=>{try{await axios.delete(`${API}/catalog/discounts/${id}`);}catch(e:any){alert(e.response?.data?.detail||'Błąd');}setConfirm(null);reload();};

  const saveProduct=async(form:any)=>{
    try{if(modal?.item?.id)await axios.put(`${API}/catalog/products/${modal.item.id}`,form);else await axios.post(`${API}/catalog/products`,form);}catch(e:any){alert(e.response?.data?.detail||'Błąd');return;}
    setModal(null);reload();};
  const savePackaging=async(form:any)=>{
    try{if(modal?.item?.id)await axios.put(`${API}/catalog/packagings/${modal.item.id}`,form);else await axios.post(`${API}/catalog/packagings`,form);}catch(e:any){alert(e.response?.data?.detail||'Błąd');return;}
    setModal(null);reload();};
  const saveSupplier=async(form:any)=>{
    try{if(modal?.item?.id)await axios.put(`${API}/catalog/suppliers/${modal.item.id}`,form);else await axios.post(`${API}/catalog/suppliers`,form);}catch(e:any){alert(e.response?.data?.detail||'Błąd');return;}
    setModal(null);reload();};
  const saveDiscount=async(form:any)=>{
    try{if(modal?.item?.id)await axios.put(`${API}/catalog/discounts/${modal.item.id}`,form);else await axios.post(`${API}/catalog/discounts`,form);}catch(e:any){alert(e.response?.data?.detail||'Błąd');return;}
    setModal(null);reload();};

  const saveCompany=async()=>{setSaving(true);try{await axios.put(`${API}/company-settings`,co);alert('Dane zapisane');}catch{alert('Błąd zapisu');}finally{setSaving(false);}};

  const toggleStock=(id:string)=>setOpenStock(prev=>prev.includes(id)?prev.filter(x=>x!==id):[...prev,id]);

  if(loading)return <div className="p-8 text-gray-400">Ładowanie...</div>;
  return(
  <div className="min-h-screen bg-gray-50" style={{fontFamily:"'Outfit',system-ui"}}>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet"/>
    <nav className="bg-gray-950 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3"><button onClick={()=>nav('/offer')} className="flex items-center gap-3"><div className="w-7 h-7 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600"/><span className="text-white font-bold">DiWine</span></button><span className="text-gray-600 text-sm">/ Ustawienia</span></div>
      <div className="flex items-center gap-1">
        <button onClick={()=>nav('/offer/list')} className="px-4 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg">Oferty</button>
        <button onClick={()=>nav('/offer/orders')} className="px-4 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg">Zamówienia</button>
        <button className="px-4 py-1.5 text-sm text-white bg-white/10 rounded-lg">Ustawienia</button>
      </div>
    </nav>
    <div className="max-w-5xl mx-auto px-6 py-6">
      <div className="flex gap-1 mb-6 bg-white rounded-xl border border-gray-200 p-1 overflow-x-auto">
        {TABS.map(t=><button key={t.id} onClick={()=>setTab(t.id)} className={`px-2 py-2 rounded-lg text-[11px] font-semibold whitespace-nowrap ${tab===t.id?'bg-indigo-600 text-white':'text-gray-500 hover:bg-gray-50'}`}>{t.label}</button>)}
      </div>

      {/* ═══ WINA ═══ */}
      {tab==='wines'&&<div>
        <TabHeader title="Wina" count={wines.length} onAdd={()=>setModal({type:'product',item:{category:'wine'}})}/>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Nazwa</th><th className="text-left p-3 text-xs text-gray-500">Kolor</th><th className="text-left p-3 text-xs text-gray-500">Typ</th><th className="text-right p-3 text-xs text-gray-500">Cena</th><th className="text-right p-3 text-xs text-gray-500">Stan</th><th className="text-right p-3 text-xs text-gray-500">Akcje</th></tr></thead>
        <tbody>{wines.map(w=><tr key={w.id} className="border-b last:border-0 hover:bg-gray-50"><td className="p-3 font-medium">{w.name}</td><td className="p-3"><div className="flex items-center gap-2"><span className="w-4 h-4 rounded-full border" style={{background:WC[w.wine_color]||'#ccc'}}/><span className="text-gray-500 text-xs">{w.wine_color}</span></div></td><td className="p-3 text-gray-500">{w.wine_type}</td><td className="p-3 text-right font-semibold">{w.base_price.toFixed(2)} zł</td><td className="p-3 text-right"><span className={`font-medium ${w.stock_quantity>0?'text-green-600':'text-red-500'}`}>{w.stock_quantity}</span></td><td className="p-3 text-right"><ActionBtns onEdit={()=>setModal({type:'product',item:w})} onDelete={()=>setConfirm({msg:`Usunąć "${w.name}"?`,onYes:()=>deleteProduct(w.id)})}/></td></tr>)}</tbody></table></div>
      </div>}

      {/* ═══ SŁODYCZE ═══ */}
      {tab==='sweets'&&<div>
        <TabHeader title="Słodycze" count={sweets.length} onAdd={()=>setModal({type:'product',item:{category:'sweet'}})}/>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Nazwa</th><th className="text-left p-3 text-xs text-gray-500">Kolor</th><th className="text-right p-3 text-xs text-gray-500">Cena</th><th className="text-right p-3 text-xs text-gray-500">Stan</th><th className="text-right p-3 text-xs text-gray-500">Akcje</th></tr></thead>
        <tbody>{expandColors(sweets).map((s,i)=><tr key={`${s.id}-${s._color||i}`} className="border-b last:border-0 hover:bg-gray-50"><td className="p-3 font-medium">{s._name}</td><td className="p-3">{s._color&&<span className="w-4 h-4 rounded-full border border-gray-200 inline-block" style={{background:SC[s._color]||'#ccc'}}/>}</td><td className="p-3 text-right font-semibold">{s.base_price.toFixed(2)} zł</td><td className="p-3 text-right"><span className={`font-medium ${s.stock_quantity>0?'text-green-600':'text-red-500'}`}>{s.stock_quantity}</span></td><td className="p-3 text-right"><ActionBtns onEdit={()=>setModal({type:'product',item:s})} onDelete={()=>setConfirm({msg:`Usunąć "${s.name}"?`,onYes:()=>deleteProduct(s.id)})}/></td></tr>)}</tbody></table></div>
      </div>}

      {/* ═══ PERSONALIZACJA ═══ */}
      {tab==='personalization'&&<div>
        <TabHeader title="Personalizacja" count={pers.length} onAdd={()=>setModal({type:'product',item:{category:'personalization'}})}/>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden mb-6"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Nazwa</th><th className="text-right p-3 text-xs text-gray-500">Cena bazowa</th><th className="text-right p-3 text-xs text-gray-500">Akcje</th></tr></thead>
        <tbody>{pers.map(p=><tr key={p.id} className="border-b last:border-0 hover:bg-gray-50"><td className="p-3 font-medium">{p.name}</td><td className="p-3 text-right font-semibold">{p.base_price.toFixed(2)} zł</td><td className="p-3 text-right"><ActionBtns onEdit={()=>setModal({type:'product',item:p})} onDelete={()=>setConfirm({msg:`Usunąć "${p.name}"?`,onYes:()=>deleteProduct(p.id)})}/></td></tr>)}</tbody></table></div>
        <div className="flex items-center justify-between mb-3"><h3 className="text-sm font-bold text-gray-500">PROGI CENOWE PERSONALIZACJI</h3><button onClick={()=>setModal({type:'discount',item:{rule_type:'personalization'}})} className="px-3 py-1 text-xs font-bold bg-indigo-600 text-white rounded-lg">+ Dodaj próg</button></div>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Zakres</th><th className="text-right p-3 text-xs text-gray-500">Cena</th><th className="text-right p-3 text-xs text-gray-500">Akcje</th></tr></thead>
        <tbody>{discs.filter(d=>d.rule_type==='personalization').map(d=><tr key={d.id} className="border-b last:border-0"><td className="p-3">{d.min_quantity}–{d.max_quantity>9000?'∞':d.max_quantity} szt.</td><td className="p-3 text-right font-semibold">{d.fixed_price?.toFixed(2)} zł</td><td className="p-3 text-right"><ActionBtns onEdit={()=>setModal({type:'discount',item:d})} onDelete={()=>setConfirm({msg:`Usunąć próg ${d.min_quantity}–${d.max_quantity}?`,onYes:()=>deleteDiscount(d.id)})}/></td></tr>)}</tbody></table></div>
      </div>}

      {/* ═══ DODATKI ═══ */}
      {tab==='deco'&&<div>
        <TabHeader title="Dodatki" count={decos.length} onAdd={()=>setModal({type:'product',item:{category:'decoration'}})}/>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Nazwa</th><th className="text-left p-3 text-xs text-gray-500">Kolor</th><th className="text-right p-3 text-xs text-gray-500">Cena</th><th className="text-right p-3 text-xs text-gray-500">Stan</th><th className="text-right p-3 text-xs text-gray-500">Akcje</th></tr></thead>
        <tbody>{expandColors(decos).map((s,i)=><tr key={`${s.id}-${s._color||i}`} className="border-b last:border-0 hover:bg-gray-50"><td className="p-3 font-medium">{s._name}</td><td className="p-3">{s._color&&<span className="w-4 h-4 rounded-full border border-gray-200 inline-block" style={{background:SC[s._color]||'#ccc'}}/>}</td><td className="p-3 text-right font-semibold">{s.base_price.toFixed(2)} zł</td><td className="p-3 text-right"><span className={`font-medium ${s.stock_quantity>0?'text-green-600':'text-red-500'}`}>{s.stock_quantity}</span></td><td className="p-3 text-right"><ActionBtns onEdit={()=>setModal({type:'product',item:s})} onDelete={()=>setConfirm({msg:`Usunąć "${s.name}"?`,onYes:()=>deleteProduct(s.id)})}/></td></tr>)}</tbody></table></div>
      </div>}

      {/* ═══ OPAKOWANIA ═══ */}
      {tab==='packaging'&&<div>
        <TabHeader title="Opakowania" count={pkgs.length} onAdd={()=>setModal({type:'packaging',item:null})}/>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Nazwa</th><th className="text-left p-3 text-xs text-gray-500">Typ</th><th className="text-center p-3 text-xs text-gray-500">But.</th><th className="text-center p-3 text-xs text-gray-500">Sloty</th><th className="text-right p-3 text-xs text-gray-500">Cena</th><th className="text-right p-3 text-xs text-gray-500">Stan</th><th className="text-right p-3 text-xs text-gray-500">Akcje</th></tr></thead>
        <tbody>{pkgs.map(p=><tr key={p.id} className="border-b last:border-0 hover:bg-gray-50"><td className="p-3 font-medium">{p.name}</td><td className="p-3 text-gray-500">{p.packaging_type}</td><td className="p-3 text-center font-semibold">{p.bottles}</td><td className="p-3 text-center">{p.sweet_slots}</td><td className="p-3 text-right font-semibold">{p.price.toFixed(2)} zł</td><td className="p-3 text-right"><span className={`font-medium ${p.stock_quantity>0?'text-green-600':'text-red-500'}`}>{p.stock_quantity}</span></td><td className="p-3 text-right"><ActionBtns onEdit={()=>setModal({type:'packaging',item:p})} onDelete={()=>setConfirm({msg:`Usunąć "${p.name}"?`,onYes:()=>deletePackaging(p.id)})}/></td></tr>)}</tbody></table></div>
      </div>}

      {/* ═══ RABATY (tylko wino) ═══ */}
      {tab==='discounts'&&<div>
        <TabHeader title="Rabaty ilościowe — Wino" count={discs.filter(d=>d.rule_type==='wine').length} onAdd={()=>setModal({type:'discount',item:{rule_type:'wine'}})}/>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Od szt.</th><th className="text-left p-3 text-xs text-gray-500">Do szt.</th><th className="text-left p-3 text-xs text-gray-500">Rabat %</th><th className="text-right p-3 text-xs text-gray-500">Akcje</th></tr></thead>
        <tbody>{discs.filter(d=>d.rule_type==='wine').map(d=><tr key={d.id} className="border-b last:border-0 hover:bg-gray-50"><td className="p-3 font-medium">{d.min_quantity}</td><td className="p-3">{d.max_quantity>9000?'∞':d.max_quantity}</td><td className="p-3 font-bold text-indigo-700">{d.discount_percent}%</td><td className="p-3 text-right"><ActionBtns onEdit={()=>setModal({type:'discount',item:d})} onDelete={()=>setConfirm({msg:`Usunąć próg ${d.min_quantity}–${d.max_quantity}?`,onYes:()=>deleteDiscount(d.id)})}/></td></tr>)}</tbody></table></div>
      </div>}

      {/* ═══ STANY MAGAZYNOWE ═══ */}
      {tab==='stock'&&<div className="space-y-2"><h2 className="text-lg font-bold text-gray-900 mb-4">Stany magazynowe</h2>
        {[{id:'wines',title:'WINA',items:wines,max:500},{id:'sweets',title:'SŁODYCZE',items:sweets,max:1000},{id:'decos',title:'DODATKI',items:decos,max:800},{id:'pkgs',title:'OPAKOWANIA',items:pkgs,max:400}].map(sec=>(
          <div key={sec.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <button onClick={()=>toggleStock(sec.id)} className="w-full flex items-center justify-between px-5 py-3 hover:bg-gray-50">
              <span className="text-xs font-bold text-gray-500">{sec.title} ({sec.items.length})</span>
              <span className={`text-gray-400 transition-transform ${openStock.includes(sec.id)?'rotate-180':''}`}>&#9662;</span>
            </button>
            {openStock.includes(sec.id)&&<div className="border-t">{sec.items.map((p:any)=>(
              <div key={p.id} className="flex items-center justify-between px-5 py-2 hover:bg-gray-50"><span className="text-sm font-medium flex-1">{p.name}</span><div className="flex items-center gap-3"><div className="w-24 bg-gray-200 rounded-full h-2"><div className={`h-2 rounded-full ${(p.stock_quantity||0)>sec.max*0.3?'bg-green-500':(p.stock_quantity||0)>0?'bg-amber-400':'bg-red-500'}`} style={{width:`${Math.min(((p.stock_quantity||0)/sec.max)*100,100)}%`}}/></div><span className={`text-sm font-bold w-12 text-right ${(p.stock_quantity||0)>0?'text-gray-900':'text-red-500'}`}>{p.stock_quantity||0}</span></div></div>
            ))}</div>}
          </div>
        ))}
      </div>}

      {/* ═══ DOSTAWCY ═══ */}
      {tab==='suppliers'&&<div>
        <TabHeader title="Dostawcy" count={sups.length} onAdd={()=>setModal({type:'supplier',item:null})}/>
        {sups.length===0?<div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">Brak dostawców</div>
        :<div className="bg-white rounded-xl border border-gray-200 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Nazwa</th><th className="text-left p-3 text-xs text-gray-500">Email</th><th className="text-left p-3 text-xs text-gray-500">Telefon</th><th className="text-right p-3 text-xs text-gray-500">Dostawa</th><th className="text-right p-3 text-xs text-gray-500">Akcje</th></tr></thead>
        <tbody>{sups.map((s:any)=><tr key={s.id} className="border-b last:border-0 hover:bg-gray-50"><td className="p-3 font-medium"><button onClick={()=>setModal({type:'supplier_detail',item:s})} className="text-indigo-600 hover:underline">{s.name}</button></td><td className="p-3 text-gray-500">{s.contact_email||'—'}</td><td className="p-3 text-gray-500">{s.contact_phone||'—'}</td><td className="p-3 text-right">{s.delivery_days} dni</td><td className="p-3 text-right"><ActionBtns onEdit={()=>setModal({type:'supplier',item:s})} onDelete={()=>setConfirm({msg:`Usunąć dostawcę "${s.name}"?`,onYes:()=>deleteSupplier(s.id)})}/></td></tr>)}</tbody></table></div>}
      </div>}

      {/* ═══ DANE DIWINE ═══ */}
      {tab==='company'&&<div><h2 className="text-lg font-bold text-gray-900 mb-4">Dane firmowe DiWine</h2>
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4"><div className="text-xs font-bold text-gray-500 mb-3">DANE REJESTROWE</div>
          <div className="grid grid-cols-3 gap-3">
            <div className="col-span-2"><label className={LBL}>Nazwa</label><input className={INP} value={co.name||''} onChange={e=>setCo({...co,name:e.target.value})}/></div>
            <div><label className={LBL}>Forma prawna</label><input className={INP} value={co.legal_form||''} onChange={e=>setCo({...co,legal_form:e.target.value})}/></div>
            <div><label className={LBL}>NIP</label><input className={INP} value={co.nip||''} onChange={e=>setCo({...co,nip:e.target.value})}/></div>
            <div><label className={LBL}>Email</label><input className={INP} value={co.email||''} onChange={e=>setCo({...co,email:e.target.value})}/></div>
            <div><label className={LBL}>www</label><input className={INP} value={co.www||''} onChange={e=>setCo({...co,www:e.target.value})}/></div>
          </div></div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4"><div className="text-xs font-bold text-gray-500 mb-3">ADRES REJESTROWY</div>
          <div className="grid grid-cols-4 gap-3">
            <div className="col-span-2"><label className={LBL}>Ulica</label><input className={INP} value={co.reg_street||''} onChange={e=>setCo({...co,reg_street:e.target.value})}/></div>
            <div><label className={LBL}>Numer</label><input className={INP} value={co.reg_number||''} onChange={e=>setCo({...co,reg_number:e.target.value})}/></div>
            <div><label className={LBL}>Kod</label><input className={INP} value={co.reg_postal||''} onChange={e=>setCo({...co,reg_postal:e.target.value})}/></div>
          </div>
          <div className="mt-3"><label className={LBL}>Miasto</label><input className={INP} value={co.reg_city||''} onChange={e=>setCo({...co,reg_city:e.target.value})}/></div></div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4"><div className="text-xs font-bold text-gray-500 mb-3">OSOBA ZAMAWIAJĄCA</div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className={LBL}>Imię</label><input className={INP} value={co.person_first_name||''} onChange={e=>setCo({...co,person_first_name:e.target.value})}/></div>
            <div><label className={LBL}>Nazwisko</label><input className={INP} value={co.person_last_name||''} onChange={e=>setCo({...co,person_last_name:e.target.value})}/></div>
            <div><label className={LBL}>Telefon</label><input className={INP} value={co.person_phone||''} onChange={e=>setCo({...co,person_phone:e.target.value})}/></div>
            <div><label className={LBL}>Email</label><input className={INP} value={co.person_email||''} onChange={e=>setCo({...co,person_email:e.target.value})}/></div>
          </div></div>
        <button onClick={saveCompany} disabled={saving} className={`px-6 py-2.5 text-sm font-bold rounded-lg ${saving?'bg-gray-300 text-gray-500':'bg-indigo-600 text-white hover:bg-indigo-700'}`}>{saving?'Zapisuję...':'Zapisz dane'}</button>
      </div>}

      {/* ═══ GRAFIKI ═══ */}
      {tab==='graphics'&&<div><h2 className="text-lg font-bold text-gray-900 mb-4">Grafiki firmowe DiWine</h2>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-white rounded-xl border border-gray-200 p-5"><div className="text-xs font-bold text-gray-500 mb-3">LOGOTYPY</div><div className="text-center py-4 text-gray-300 text-sm mb-3">Logotypy DiWine (kolorowe, białe, ciemne)</div><UploadBtn label="+ Wgraj logo" endpoint={`${API}/photos/upload?category=diwine_logo`} onDone={reload}/></div>
          <div className="bg-white rounded-xl border border-gray-200 p-5"><div className="text-xs font-bold text-gray-500 mb-3">GRAFIKI</div><div className="text-center py-4 text-gray-300 text-sm mb-3">Tła, wzory, grafiki dekoracyjne</div><UploadBtn label="+ Wgraj grafikę" endpoint={`${API}/photos/upload?category=diwine_graphics`} onDone={reload}/></div>
        </div>
        {(()=>{const f=photos.filter((p:any)=>p.category==='diwine_logo'||p.category==='diwine_graphics');if(!f.length)return null;return<div className="grid grid-cols-6 gap-2">{f.map((p:any)=><div key={p.id} className="rounded-lg border border-gray-200 overflow-hidden"><img src={p.thumbnail_url||p.url} alt="" className="w-full aspect-square object-cover"/><div className="p-1 text-[9px] text-gray-400 text-center">{p.category.replace('diwine_','')}</div></div>)}</div>;})()}
      </div>}

      {/* ═══ LOGO KLIENTÓW ═══ */}
      {tab==='client_logos'&&<div><h2 className="text-lg font-bold text-gray-900 mb-4">Logo klientów</h2>
        {clients.length===0?<div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">Brak klientów</div>
        :<div className="bg-white rounded-xl border border-gray-200 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Firma</th><th className="text-left p-3 text-xs text-gray-500">NIP</th><th className="text-center p-3 text-xs text-gray-500">Logo</th></tr></thead>
        <tbody>{clients.map((c:any)=><tr key={c.id} className="border-b last:border-0 hover:bg-gray-50"><td className="p-3 font-medium">{c.company_name}</td><td className="p-3 text-gray-500">{c.nip||'—'}</td><td className="p-3 text-center">{c.logo_url?<img src={c.logo_url} alt="" className="h-8 mx-auto"/>:<span className="text-gray-300 text-xs">—</span>}</td></tr>)}</tbody></table></div>}
      </div>}

      {/* ═══ ZDJĘCIA ═══ */}
      {tab==='photos'&&<div>
        <div className="flex items-center justify-between mb-4"><h2 className="text-lg font-bold text-gray-900">Baza zdjęć ({photos.length})</h2><UploadBtn label="+ Wgraj zdjęcie" endpoint={`${API}/photos/upload?category=custom`} onDone={reload}/></div>
        <div className="flex gap-2 mb-4">{([{id:'unsplash' as const,l:`Unsplash (${photos.filter((p:any)=>p.source==='unsplash').length})`},{id:'diwine' as const,l:`DiWine (${photos.filter((p:any)=>['upload','diwine'].includes(p.source||'')).length})`},{id:'inne' as const,l:`Inne (${photos.filter((p:any)=>!['unsplash','upload','diwine'].includes(p.source||'')).length})`}]).map(t=><button key={t.id} onClick={()=>setPhotoTab(t.id)} className={`px-4 py-2 rounded-lg text-xs font-semibold ${photoTab===t.id?'bg-indigo-100 text-indigo-700':'bg-gray-100 text-gray-500'}`}>{t.l}</button>)}</div>
        {(()=>{const sh=photoTab==='unsplash'?photos.filter((p:any)=>p.source==='unsplash'):photoTab==='diwine'?photos.filter((p:any)=>['upload','diwine'].includes(p.source||'')):photos.filter((p:any)=>!['unsplash','upload','diwine'].includes(p.source||''));
        if(!sh.length)return<div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">Brak zdjęć</div>;
        return<div className="grid grid-cols-4 gap-3">{sh.map((p:any)=><div key={p.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden group"><div className="aspect-video overflow-hidden"><img src={p.thumbnail_url||p.url} alt="" className="w-full h-full object-cover group-hover:scale-105 transition-transform"/></div><div className="p-2"><div className="flex items-center gap-1 flex-wrap"><span className="text-[9px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">{p.category}</span>{(p.tags||[]).slice(0,3).map((t:string)=><span key={t} className="text-[9px] px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-600">{t}</span>)}</div></div></div>)}</div>;})()}
      </div>}
    </div>

    {/* ═══ MODALE ═══ */}
    {confirm&&<ConfirmDialog msg={confirm.msg} onYes={confirm.onYes} onNo={()=>setConfirm(null)}/>}

    {/* Supplier detail (read-only) */}
    {modal?.type==='supplier_detail'&&<Modal title={modal.item.name} onClose={()=>setModal(null)}>
      <div className="space-y-3 text-sm">
        {modal.item.nip&&<div><span className="text-gray-400">NIP:</span> <span className="font-medium">{modal.item.nip}</span></div>}
        {modal.item.contact_email&&<div><span className="text-gray-400">Email:</span> <span className="font-medium">{modal.item.contact_email}</span></div>}
        {modal.item.contact_phone&&<div><span className="text-gray-400">Telefon:</span> <span className="font-medium">{modal.item.contact_phone}</span></div>}
        {(modal.item.address_street||modal.item.address_city)&&<div><span className="text-gray-400">Adres:</span> <span className="font-medium">{[modal.item.address_street,modal.item.address_number].filter(Boolean).join(' ')}{modal.item.address_city?`, ${modal.item.address_postal_code||''} ${modal.item.address_city}`:''}</span></div>}
        {modal.item.www&&<div><span className="text-gray-400">www:</span> <a href={modal.item.www.startsWith('http')?modal.item.www:`https://${modal.item.www}`} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline font-medium">{modal.item.www}</a></div>}
        <div><span className="text-gray-400">Czas dostawy:</span> <span className="font-medium">{modal.item.delivery_days} dni</span></div>
      </div>
    </Modal>}

    {/* Supplier edit/create */}
    {modal?.type==='supplier'&&<SupplierForm item={modal.item} onSave={saveSupplier} onClose={()=>setModal(null)}/>}

    {/* Product edit/create */}
    {modal?.type==='product'&&<ProductForm item={modal.item} sups={sups} onSave={saveProduct} onClose={()=>setModal(null)}/>}

    {/* Packaging edit/create */}
    {modal?.type==='packaging'&&<PackagingForm item={modal.item} onSave={savePackaging} onClose={()=>setModal(null)}/>}

    {/* Discount edit/create */}
    {modal?.type==='discount'&&<DiscountForm item={modal.item} onSave={saveDiscount} onClose={()=>setModal(null)}/>}
  </div>);
}

/* ─── FORM MODALS ─── */

function ProductForm({item,sups,onSave,onClose}:{item:any;sups:any[];onSave:(d:any)=>void;onClose:()=>void}){
  const [f,setF]=useState({
    name:item?.name||'',category:item?.category||'wine',base_price:item?.base_price||0,
    wine_color:item?.wine_color||'',wine_type:item?.wine_type||'',
    slot_size:item?.slot_size??1,available_colors_json:item?.available_colors_json||[],
    stock_quantity:item?.stock_quantity||0,supplier_id:item?.supplier_id||'',description:item?.description||'',
  });
  const isWine=f.category==='wine';const hasColors=['sweet','decoration'].includes(f.category);
  const toggleColor=(c:string)=>setF(p=>({...p,available_colors_json:p.available_colors_json.includes(c)?p.available_colors_json.filter((x:string)=>x!==c):[...p.available_colors_json,c]}));
  return(<Modal title={item?.id?'Edytuj produkt':'Nowy produkt'} onClose={onClose}><div className="space-y-3">
    <div><label className={LBL}>Nazwa</label><input className={INP} value={f.name} onChange={e=>setF({...f,name:e.target.value})}/></div>
    <div><label className={LBL}>Kategoria</label><select className={INP} value={f.category} onChange={e=>setF({...f,category:e.target.value})}><option value="wine">Wino</option><option value="sweet">Słodycze</option><option value="decoration">Dodatki</option><option value="personalization">Personalizacja</option></select></div>
    {isWine&&<div className="grid grid-cols-2 gap-3">
      <div><label className={LBL}>Kolor wina</label><select className={INP} value={f.wine_color} onChange={e=>setF({...f,wine_color:e.target.value})}><option value="">—</option>{Object.keys(WC).map(c=><option key={c} value={c}>{c}</option>)}</select></div>
      <div><label className={LBL}>Typ</label><select className={INP} value={f.wine_type} onChange={e=>setF({...f,wine_type:e.target.value})}><option value="">—</option><option value="wytrawne">wytrawne</option><option value="półwytrawne">półwytrawne</option><option value="półsłodkie">półsłodkie</option><option value="słodkie">słodkie</option><option value="musujące">musujące</option></select></div>
    </div>}
    {hasColors&&<div><label className={LBL}>Kolory</label><div className="flex gap-2 flex-wrap">{Object.entries(SC).map(([c,hex])=><button key={c} type="button" onClick={()=>toggleColor(c)} className={`flex items-center gap-1.5 px-2 py-1 rounded-lg border text-xs ${f.available_colors_json.includes(c)?'border-indigo-400 bg-indigo-50':'border-gray-200'}`}><span className="w-3 h-3 rounded-full border" style={{background:hex}}/>{COLOR_NAMES[c]||c}</button>)}</div></div>}
    <div className="grid grid-cols-2 gap-3">
      <div><label className={LBL}>Cena bazowa</label><input type="number" step="0.01" className={INP} value={f.base_price} onChange={e=>setF({...f,base_price:parseFloat(e.target.value)||0})}/></div>
      <div><label className={LBL}>Stan mag.</label><input type="number" className={INP} value={f.stock_quantity} onChange={e=>setF({...f,stock_quantity:parseInt(e.target.value)||0})}/></div>
    </div>
    {sups.length>0&&<div><label className={LBL}>Dostawca</label><select className={INP} value={f.supplier_id} onChange={e=>setF({...f,supplier_id:e.target.value})}><option value="">— brak —</option>{sups.map((s:any)=><option key={s.id} value={s.id}>{s.name}</option>)}</select></div>}
    <div className="flex justify-end gap-3 pt-3">
      <button onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">Anuluj</button>
      <button onClick={()=>onSave(f)} className="px-4 py-2 text-sm font-bold bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Zapisz</button>
    </div>
  </div></Modal>);
}

function PackagingForm({item,onSave,onClose}:{item:any;onSave:(d:any)=>void;onClose:()=>void}){
  const [f,setF]=useState({name:item?.name||'',packaging_type:item?.packaging_type||'pudełko_czarne',bottles:item?.bottles||1,sweet_slots:item?.sweet_slots||5,price:item?.price||0,stock_quantity:item?.stock_quantity||0});
  return(<Modal title={item?.id?'Edytuj opakowanie':'Nowe opakowanie'} onClose={onClose}><div className="space-y-3">
    <div><label className={LBL}>Nazwa</label><input className={INP} value={f.name} onChange={e=>setF({...f,name:e.target.value})}/></div>
    <div><label className={LBL}>Typ</label><select className={INP} value={f.packaging_type} onChange={e=>setF({...f,packaging_type:e.target.value})}><option value="pudełko_czarne">pudełko czarne</option><option value="kraft">kraft</option><option value="skrzynka">skrzynka</option><option value="tuba">tuba</option><option value="box_xl">box XL</option></select></div>
    <div className="grid grid-cols-2 gap-3">
      <div><label className={LBL}>Butelki</label><input type="number" className={INP} value={f.bottles} onChange={e=>setF({...f,bottles:parseInt(e.target.value)||1})}/></div>
      <div><label className={LBL}>Sloty słodyczy</label><input type="number" className={INP} value={f.sweet_slots} onChange={e=>setF({...f,sweet_slots:parseInt(e.target.value)||0})}/></div>
    </div>
    <div className="grid grid-cols-2 gap-3">
      <div><label className={LBL}>Cena</label><input type="number" step="0.01" className={INP} value={f.price} onChange={e=>setF({...f,price:parseFloat(e.target.value)||0})}/></div>
      <div><label className={LBL}>Stan mag.</label><input type="number" className={INP} value={f.stock_quantity} onChange={e=>setF({...f,stock_quantity:parseInt(e.target.value)||0})}/></div>
    </div>
    <div className="flex justify-end gap-3 pt-3">
      <button onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">Anuluj</button>
      <button onClick={()=>onSave(f)} className="px-4 py-2 text-sm font-bold bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Zapisz</button>
    </div>
  </div></Modal>);
}

function SupplierForm({item,onSave,onClose}:{item:any;onSave:(d:any)=>void;onClose:()=>void}){
  const [f,setF]=useState({name:item?.name||'',contact_email:item?.contact_email||'',contact_phone:item?.contact_phone||'',delivery_days:item?.delivery_days||5,address_street:item?.address_street||'',address_number:item?.address_number||'',address_postal_code:item?.address_postal_code||'',address_city:item?.address_city||'',nip:item?.nip||'',www:item?.www||''});
  return(<Modal title={item?.id?'Edytuj dostawcę':'Nowy dostawca'} onClose={onClose}><div className="space-y-3">
    <div><label className={LBL}>Nazwa</label><input className={INP} value={f.name} onChange={e=>setF({...f,name:e.target.value})}/></div>
    <div className="grid grid-cols-2 gap-3">
      <div><label className={LBL}>Email</label><input className={INP} value={f.contact_email} onChange={e=>setF({...f,contact_email:e.target.value})}/></div>
      <div><label className={LBL}>Telefon</label><input className={INP} value={f.contact_phone} onChange={e=>setF({...f,contact_phone:e.target.value})}/></div>
    </div>
    <div><label className={LBL}>NIP</label><input className={INP} value={f.nip} onChange={e=>setF({...f,nip:e.target.value})}/></div>
    <div className="grid grid-cols-4 gap-3">
      <div className="col-span-2"><label className={LBL}>Ulica</label><input className={INP} value={f.address_street} onChange={e=>setF({...f,address_street:e.target.value})}/></div>
      <div><label className={LBL}>Numer</label><input className={INP} value={f.address_number} onChange={e=>setF({...f,address_number:e.target.value})}/></div>
      <div><label className={LBL}>Kod</label><input className={INP} value={f.address_postal_code} onChange={e=>setF({...f,address_postal_code:e.target.value})}/></div>
    </div>
    <div><label className={LBL}>Miasto</label><input className={INP} value={f.address_city} onChange={e=>setF({...f,address_city:e.target.value})}/></div>
    <div className="grid grid-cols-2 gap-3">
      <div><label className={LBL}>www</label><input className={INP} value={f.www} onChange={e=>setF({...f,www:e.target.value})}/></div>
      <div><label className={LBL}>Czas dostawy (dni)</label><input type="number" className={INP} value={f.delivery_days} onChange={e=>setF({...f,delivery_days:parseInt(e.target.value)||5})}/></div>
    </div>
    <div className="flex justify-end gap-3 pt-3">
      <button onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">Anuluj</button>
      <button onClick={()=>onSave(f)} className="px-4 py-2 text-sm font-bold bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Zapisz</button>
    </div>
  </div></Modal>);
}

function DiscountForm({item,onSave,onClose}:{item:any;onSave:(d:any)=>void;onClose:()=>void}){
  const isPers=item?.rule_type==='personalization';
  const [f,setF]=useState({rule_type:item?.rule_type||'wine',product_id:item?.product_id||null,min_quantity:item?.min_quantity||1,max_quantity:item?.max_quantity||99999,discount_percent:item?.discount_percent||0,fixed_price:item?.fixed_price||0});
  return(<Modal title={item?.id?'Edytuj rabat':'Nowy rabat'} onClose={onClose}><div className="space-y-3">
    <div className="grid grid-cols-2 gap-3">
      <div><label className={LBL}>Od (szt.)</label><input type="number" className={INP} value={f.min_quantity} onChange={e=>setF({...f,min_quantity:parseInt(e.target.value)||1})}/></div>
      <div><label className={LBL}>Do (szt.)</label><input type="number" className={INP} value={f.max_quantity>9000?'':f.max_quantity} placeholder="∞" onChange={e=>setF({...f,max_quantity:e.target.value?parseInt(e.target.value):99999})}/></div>
    </div>
    {isPers
      ?<div><label className={LBL}>Cena za szt.</label><input type="number" step="0.01" className={INP} value={f.fixed_price} onChange={e=>setF({...f,fixed_price:parseFloat(e.target.value)||0})}/></div>
      :<div><label className={LBL}>Rabat %</label><input type="number" step="0.1" className={INP} value={f.discount_percent} onChange={e=>setF({...f,discount_percent:parseFloat(e.target.value)||0})}/></div>
    }
    <div className="flex justify-end gap-3 pt-3">
      <button onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">Anuluj</button>
      <button onClick={()=>onSave(f)} className="px-4 py-2 text-sm font-bold bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Zapisz</button>
    </div>
  </div></Modal>);
}
