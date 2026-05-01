import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = '/api/v1/offers';
type Tab = 'wines'|'sweets'|'deco'|'packaging'|'discounts'|'stock'|'suppliers'|'company'|'graphics'|'client_logos'|'photos';
const TABS: {id:Tab;label:string}[] = [
  {id:'wines',label:'Wina'},{id:'sweets',label:'Słodycze'},{id:'deco',label:'Dodatki'},
  {id:'packaging',label:'Opakowania'},{id:'discounts',label:'Rabaty'},{id:'stock',label:'Stany'},
  {id:'suppliers',label:'Dostawcy'},{id:'company',label:'Dane DiWine'},
  {id:'graphics',label:'Grafiki'},{id:'client_logos',label:'Logo klientów'},{id:'photos',label:'Zdjęcia'},
];
const WC:Record<string,string>={czerwone:'#DC2626',białe:'#FEF9E7',różowe:'#FBCFE8',pomarańczowe:'#EA580C'};
const SC:Record<string,string>={red:'#DC2626',gold:'#D97706',green:'#16A34A',blue:'#2563EB',yellow:'#EAB308',craft:'#8B5E3C',pastel:'#F9A8D4',silver:'#9CA3AF'};

function UploadBtn({label,endpoint,onDone}:{label:string;endpoint:string;onDone:()=>void}){
  const ref=useRef<HTMLInputElement>(null);const [up,setUp]=useState(false);
  return(<>
    <input ref={ref} type="file" accept="image/*" onChange={async e=>{const f=e.target.files?.[0];if(!f)return;setUp(true);try{const fd=new FormData();fd.append('file',f);await axios.post(endpoint,fd,{headers:{'Content-Type':'multipart/form-data'}});onDone();}catch{alert('Błąd uploadu');}finally{setUp(false);if(ref.current)ref.current.value='';}}} className="hidden"/>
    <button onClick={()=>ref.current?.click()} disabled={up} className={`px-4 py-2 text-sm font-bold rounded-lg ${up?'bg-gray-300 text-gray-500':'bg-indigo-600 text-white hover:bg-indigo-700'}`}>{up?'Wgrywam...':label}</button>
  </>);
}
function StockBar({items,title,max}:{items:any[];title:string;max:number}){
  return(<div className="bg-white rounded-xl border border-gray-200 p-4"><div className="text-xs font-bold text-gray-500 mb-3">{title}</div><div className="space-y-1">{items.map((p:any)=>(
    <div key={p.id||p.name} className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-50"><span className="text-sm font-medium flex-1">{p.name}</span><div className="flex items-center gap-3"><div className="w-24 bg-gray-200 rounded-full h-2"><div className={`h-2 rounded-full ${(p.stock_quantity||0)>max*0.3?'bg-green-500':(p.stock_quantity||0)>0?'bg-amber-400':'bg-red-500'}`} style={{width:`${Math.min(((p.stock_quantity||0)/max)*100,100)}%`}}/></div><span className={`text-sm font-bold w-12 text-right ${(p.stock_quantity||0)>0?'text-gray-900':'text-red-500'}`}>{p.stock_quantity||0}</span></div></div>
  ))}</div></div>);
}

export default function OfferSettings(){
  const nav=useNavigate();const [tab,setTab]=useState<Tab>('wines');
  const [prods,setProds]=useState<any[]>([]);const [pkgs,setPkgs]=useState<any[]>([]);
  const [discs,setDiscs]=useState<any[]>([]);const [photos,setPhotos]=useState<any[]>([]);
  const [clients,setClients]=useState<any[]>([]);const [sups,setSups]=useState<any[]>([]);
  const [co,setCo]=useState<any>({});const [saving,setSaving]=useState(false);
  const [photoTab,setPhotoTab]=useState<'unsplash'|'diwine'|'inne'>('unsplash');
  const [loading,setLoading]=useState(true);

  const reload=()=>{Promise.all([
    axios.get(`${API}/catalog/products`),axios.get(`${API}/catalog/packagings`),
    axios.get(`${API}/catalog/discounts`),axios.get(`${API}/photos/library?limit=100`).catch(()=>({data:[]})),
    axios.get(`${API}/clients`).catch(()=>({data:[]})),axios.get(`${API}/catalog/suppliers`).catch(()=>({data:[]})),
    axios.get(`${API}/company-settings`).catch(()=>({data:{}})),
  ]).then(([p,pk,d,ph,cl,su,cs])=>{
    setProds(p.data);setPkgs(pk.data);setDiscs(d.data);setPhotos(ph.data);setClients(cl.data);setSups(su.data);setCo(cs.data);
  }).finally(()=>setLoading(false));};

  useEffect(()=>{setLoading(true);reload();},[]);
  const wines=prods.filter(p=>p.category==='wine'),sweets=prods.filter(p=>p.category==='sweet');
  const decos=prods.filter(p=>p.category==='decoration'),pers=prods.filter(p=>p.category==='personalization');

  const saveCompany=async()=>{setSaving(true);try{await axios.put(`${API}/company-settings`,co);alert('Dane zapisane');}catch{alert('Błąd zapisu');}finally{setSaving(false);}};

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

      {/* WINA */}
      {tab==='wines'&&<div><h2 className="text-lg font-bold text-gray-900 mb-4">Wina ({wines.length})</h2>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Nazwa</th><th className="text-left p-3 text-xs text-gray-500">Kolor</th><th className="text-left p-3 text-xs text-gray-500">Typ</th><th className="text-right p-3 text-xs text-gray-500">Cena</th><th className="text-right p-3 text-xs text-gray-500">Stan</th></tr></thead>
        <tbody>{wines.map(w=><tr key={w.id} className="border-b last:border-0 hover:bg-gray-50"><td className="p-3 font-medium">{w.name}</td><td className="p-3"><div className="flex items-center gap-2"><span className="w-4 h-4 rounded-full border" style={{background:WC[w.wine_color]||'#ccc'}}/><span className="text-gray-500 text-xs">{w.wine_color}</span></div></td><td className="p-3 text-gray-500">{w.wine_type}</td><td className="p-3 text-right font-semibold">{w.base_price.toFixed(2)} zł</td><td className="p-3 text-right"><span className={`font-medium ${w.stock_quantity>0?'text-green-600':'text-red-500'}`}>{w.stock_quantity}</span></td></tr>)}</tbody></table></div>
      </div>}

      {/* SŁODYCZE */}
      {tab==='sweets'&&<div><h2 className="text-lg font-bold text-gray-900 mb-4">Słodycze ({sweets.length})</h2>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Nazwa</th><th className="text-left p-3 text-xs text-gray-500">Kolory</th><th className="text-center p-3 text-xs text-gray-500">Sloty</th><th className="text-right p-3 text-xs text-gray-500">Cena</th><th className="text-right p-3 text-xs text-gray-500">Stan</th></tr></thead>
        <tbody>{sweets.map(s=><tr key={s.id} className="border-b last:border-0 hover:bg-gray-50"><td className="p-3 font-medium">{s.name}</td><td className="p-3"><div className="flex gap-0.5">{(s.available_colors_json||[]).map((c:string)=><span key={c} className="w-4 h-4 rounded-full border border-gray-200" style={{background:SC[c]||'#ccc'}} title={c}/>)}</div></td><td className="p-3 text-center">{s.slot_size}</td><td className="p-3 text-right font-semibold">{s.base_price.toFixed(2)} zł</td><td className="p-3 text-right"><span className={`font-medium ${s.stock_quantity>0?'text-green-600':'text-red-500'}`}>{s.stock_quantity}</span></td></tr>)}</tbody></table></div>
        {pers.length>0&&<><h3 className="text-sm font-bold text-gray-500 mt-6 mb-3">Personalizacja</h3><div className="bg-white rounded-xl border border-gray-200 overflow-hidden">{pers.map(p=><div key={p.id} className="flex items-center justify-between px-5 py-3 border-b last:border-0"><span className="font-medium">{p.name}</span><span className="font-semibold text-indigo-700">{p.base_price.toFixed(2)} zł</span></div>)}</div></>}
      </div>}

      {/* DODATKI */}
      {tab==='deco'&&<div><h2 className="text-lg font-bold text-gray-900 mb-4">Dodatki ({decos.length})</h2>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Nazwa</th><th className="text-left p-3 text-xs text-gray-500">Kolory</th><th className="text-center p-3 text-xs text-gray-500">Sloty</th><th className="text-right p-3 text-xs text-gray-500">Cena</th><th className="text-right p-3 text-xs text-gray-500">Stan</th></tr></thead>
        <tbody>{decos.map(s=><tr key={s.id} className="border-b last:border-0 hover:bg-gray-50"><td className="p-3 font-medium">{s.name}</td><td className="p-3"><div className="flex gap-0.5">{(s.available_colors_json||[]).map((c:string)=><span key={c} className="w-4 h-4 rounded-full border border-gray-200" style={{background:SC[c]||'#ccc'}} title={c}/>)}</div></td><td className="p-3 text-center">{s.slot_size}</td><td className="p-3 text-right font-semibold">{s.base_price.toFixed(2)} zł</td><td className="p-3 text-right"><span className={`font-medium ${s.stock_quantity>0?'text-green-600':'text-red-500'}`}>{s.stock_quantity}</span></td></tr>)}</tbody></table></div>
      </div>}

      {/* OPAKOWANIA */}
      {tab==='packaging'&&<div><h2 className="text-lg font-bold text-gray-900 mb-4">Opakowania ({pkgs.length})</h2>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Nazwa</th><th className="text-left p-3 text-xs text-gray-500">Typ</th><th className="text-center p-3 text-xs text-gray-500">But.</th><th className="text-center p-3 text-xs text-gray-500">Sloty</th><th className="text-right p-3 text-xs text-gray-500">Cena</th><th className="text-right p-3 text-xs text-gray-500">Stan</th></tr></thead>
        <tbody>{pkgs.map(p=><tr key={p.id} className="border-b last:border-0 hover:bg-gray-50"><td className="p-3 font-medium">{p.name}</td><td className="p-3 text-gray-500">{p.packaging_type}</td><td className="p-3 text-center font-semibold">{p.bottles}</td><td className="p-3 text-center">{p.sweet_slots}</td><td className="p-3 text-right font-semibold">{p.price.toFixed(2)} zł</td><td className="p-3 text-right"><span className={`font-medium ${p.stock_quantity>0?'text-green-600':'text-red-500'}`}>{p.stock_quantity}</span></td></tr>)}</tbody></table></div>
      </div>}

      {/* RABATY */}
      {tab==='discounts'&&<div><h2 className="text-lg font-bold text-gray-900 mb-4">Rabaty ilościowe</h2>
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4"><div className="text-xs font-bold text-gray-500 mb-3">RABAT NA WINO</div><div className="flex gap-2">{discs.filter(d=>d.rule_type==='wine').map(d=><div key={d.id} className="flex-1 bg-gray-50 rounded-lg p-3 text-center"><div className="text-xs text-gray-400">{d.min_quantity}–{d.max_quantity>9000?'∞':d.max_quantity}</div><div className="text-lg font-bold text-indigo-700">{d.discount_percent}%</div></div>)}</div></div>
        <div className="bg-white rounded-xl border border-gray-200 p-4"><div className="text-xs font-bold text-gray-500 mb-3">PERSONALIZACJA</div><table className="w-full text-sm"><tbody>{discs.filter(d=>d.rule_type==='personalization').map(d=><tr key={d.id} className="border-b last:border-0"><td className="p-2">{d.min_quantity}–{d.max_quantity>9000?'∞':d.max_quantity} szt.</td><td className="p-2 text-right font-semibold">{d.fixed_price?.toFixed(2)} zł</td></tr>)}</tbody></table></div>
      </div>}

      {/* STANY */}
      {tab==='stock'&&<div className="space-y-4"><h2 className="text-lg font-bold text-gray-900">Stany magazynowe</h2>
        <StockBar title="WINA" items={wines} max={500}/><StockBar title="SŁODYCZE" items={sweets} max={1000}/>
        <StockBar title="DODATKI" items={decos} max={800}/><StockBar title="OPAKOWANIA" items={pkgs} max={400}/>
      </div>}

      {/* DOSTAWCY */}
      {tab==='suppliers'&&<div><h2 className="text-lg font-bold text-gray-900 mb-4">Dostawcy ({sups.length})</h2>
        {sups.length===0?<div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">Brak dostawców</div>
        :<div className="bg-white rounded-xl border border-gray-200 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Nazwa</th><th className="text-left p-3 text-xs text-gray-500">Email</th><th className="text-left p-3 text-xs text-gray-500">Telefon</th><th className="text-right p-3 text-xs text-gray-500">Czas dostawy</th></tr></thead>
        <tbody>{sups.map((s:any)=><tr key={s.id} className="border-b last:border-0 hover:bg-gray-50"><td className="p-3 font-medium">{s.name}</td><td className="p-3 text-gray-500">{s.contact_email||'—'}</td><td className="p-3 text-gray-500">{s.contact_phone||'—'}</td><td className="p-3 text-right">{s.delivery_days||'—'} dni</td></tr>)}</tbody></table></div>}
      </div>}

      {/* DANE DIWINE */}
      {tab==='company'&&<div><h2 className="text-lg font-bold text-gray-900 mb-4">Dane firmowe DiWine</h2>
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4"><div className="text-xs font-bold text-gray-500 mb-3">DANE REJESTROWE</div>
          <div className="grid grid-cols-3 gap-3">
            <div className="col-span-2"><label className="text-[10px] text-gray-400 block mb-0.5">Nazwa</label><input className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={co.name||''} onChange={e=>setCo({...co,name:e.target.value})}/></div>
            <div><label className="text-[10px] text-gray-400 block mb-0.5">Forma prawna</label><input className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={co.legal_form||''} onChange={e=>setCo({...co,legal_form:e.target.value})}/></div>
            <div><label className="text-[10px] text-gray-400 block mb-0.5">NIP</label><input className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={co.nip||''} onChange={e=>setCo({...co,nip:e.target.value})}/></div>
            <div><label className="text-[10px] text-gray-400 block mb-0.5">Email</label><input className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={co.email||''} onChange={e=>setCo({...co,email:e.target.value})}/></div>
            <div><label className="text-[10px] text-gray-400 block mb-0.5">www</label><input className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={co.www||''} onChange={e=>setCo({...co,www:e.target.value})}/></div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4"><div className="text-xs font-bold text-gray-500 mb-3">ADRES REJESTROWY</div>
          <div className="grid grid-cols-4 gap-3">
            <div className="col-span-2"><label className="text-[10px] text-gray-400 block mb-0.5">Ulica</label><input className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={co.reg_street||''} onChange={e=>setCo({...co,reg_street:e.target.value})}/></div>
            <div><label className="text-[10px] text-gray-400 block mb-0.5">Numer</label><input className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={co.reg_number||''} onChange={e=>setCo({...co,reg_number:e.target.value})}/></div>
            <div><label className="text-[10px] text-gray-400 block mb-0.5">Kod</label><input className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={co.reg_postal||''} onChange={e=>setCo({...co,reg_postal:e.target.value})}/></div>
          </div>
          <div className="mt-3"><label className="text-[10px] text-gray-400 block mb-0.5">Miasto</label><input className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={co.reg_city||''} onChange={e=>setCo({...co,reg_city:e.target.value})}/></div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4"><div className="text-xs font-bold text-gray-500 mb-3">OSOBA ZAMAWIAJĄCA</div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="text-[10px] text-gray-400 block mb-0.5">Imię</label><input className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={co.person_first_name||''} onChange={e=>setCo({...co,person_first_name:e.target.value})}/></div>
            <div><label className="text-[10px] text-gray-400 block mb-0.5">Nazwisko</label><input className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={co.person_last_name||''} onChange={e=>setCo({...co,person_last_name:e.target.value})}/></div>
            <div><label className="text-[10px] text-gray-400 block mb-0.5">Telefon</label><input className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={co.person_phone||''} onChange={e=>setCo({...co,person_phone:e.target.value})}/></div>
            <div><label className="text-[10px] text-gray-400 block mb-0.5">Email</label><input className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={co.person_email||''} onChange={e=>setCo({...co,person_email:e.target.value})}/></div>
          </div>
        </div>
        <button onClick={saveCompany} disabled={saving} className={`px-6 py-2.5 text-sm font-bold rounded-lg ${saving?'bg-gray-300 text-gray-500':'bg-indigo-600 text-white hover:bg-indigo-700'}`}>{saving?'Zapisuję...':'Zapisz dane'}</button>
      </div>}

      {/* GRAFIKI DIWINE */}
      {tab==='graphics'&&<div><h2 className="text-lg font-bold text-gray-900 mb-4">Grafiki firmowe DiWine</h2>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-white rounded-xl border border-gray-200 p-5"><div className="text-xs font-bold text-gray-500 mb-3">LOGOTYPY</div><div className="text-center py-4 text-gray-300 text-sm mb-3">Logotypy DiWine (kolorowe, białe, ciemne)</div><UploadBtn label="+ Wgraj logo" endpoint={`${API}/photos/upload?category=diwine_logo`} onDone={reload}/></div>
          <div className="bg-white rounded-xl border border-gray-200 p-5"><div className="text-xs font-bold text-gray-500 mb-3">GRAFIKI</div><div className="text-center py-4 text-gray-300 text-sm mb-3">Tła, wzory, grafiki dekoracyjne</div><UploadBtn label="+ Wgraj grafikę" endpoint={`${API}/photos/upload?category=diwine_graphics`} onDone={reload}/></div>
        </div>
        {(()=>{const f=photos.filter(p=>p.category==='diwine_logo'||p.category==='diwine_graphics');if(!f.length)return null;return<div className="grid grid-cols-6 gap-2">{f.map((p:any)=><div key={p.id} className="rounded-lg border border-gray-200 overflow-hidden"><img src={p.thumbnail_url||p.url} alt="" className="w-full aspect-square object-cover"/><div className="p-1 text-[9px] text-gray-400 text-center">{p.category.replace('diwine_','')}</div></div>)}</div>;})()}
      </div>}

      {/* LOGO KLIENTÓW */}
      {tab==='client_logos'&&<div><h2 className="text-lg font-bold text-gray-900 mb-4">Logo klientów</h2>
        {clients.length===0?<div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">Brak klientów</div>
        :<div className="bg-white rounded-xl border border-gray-200 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-gray-50 border-b"><th className="text-left p-3 text-xs text-gray-500">Firma</th><th className="text-left p-3 text-xs text-gray-500">NIP</th><th className="text-center p-3 text-xs text-gray-500">Logo</th></tr></thead>
        <tbody>{clients.map((c:any)=><tr key={c.id} className="border-b last:border-0 hover:bg-gray-50"><td className="p-3 font-medium">{c.company_name}</td><td className="p-3 text-gray-500">{c.nip||'—'}</td><td className="p-3 text-center">{c.logo_url?<img src={c.logo_url} alt="" className="h-8 mx-auto"/>:<span className="text-gray-300 text-xs">—</span>}</td></tr>)}</tbody></table></div>}
      </div>}

      {/* ZDJĘCIA */}
      {tab==='photos'&&<div>
        <div className="flex items-center justify-between mb-4"><h2 className="text-lg font-bold text-gray-900">Baza zdjęć</h2><UploadBtn label="+ Wgraj zdjęcie" endpoint={`${API}/photos/upload?category=custom`} onDone={reload}/></div>
        <div className="flex gap-2 mb-4">{([{id:'unsplash' as const,l:`Unsplash (${photos.filter(p=>p.source==='unsplash').length})`},{id:'diwine' as const,l:`DiWine (${photos.filter(p=>['upload','diwine'].includes(p.source||'')).length})`},{id:'inne' as const,l:`Inne (${photos.filter(p=>!['unsplash','upload','diwine'].includes(p.source||'')).length})`}]).map(t=><button key={t.id} onClick={()=>setPhotoTab(t.id)} className={`px-4 py-2 rounded-lg text-xs font-semibold ${photoTab===t.id?'bg-indigo-100 text-indigo-700':'bg-gray-100 text-gray-500'}`}>{t.l}</button>)}</div>
        {(()=>{const sh=photoTab==='unsplash'?photos.filter(p=>p.source==='unsplash'):photoTab==='diwine'?photos.filter(p=>['upload','diwine'].includes(p.source||'')):photos.filter(p=>!['unsplash','upload','diwine'].includes(p.source||''));
        if(!sh.length)return<div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">Brak zdjęć</div>;
        return<div className="grid grid-cols-4 gap-3">{sh.map((p:any)=><div key={p.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden group"><div className="aspect-video overflow-hidden"><img src={p.thumbnail_url||p.url} alt="" className="w-full h-full object-cover group-hover:scale-105 transition-transform"/></div><div className="p-2"><div className="flex items-center gap-1 flex-wrap"><span className="text-[9px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">{p.category}</span>{(p.tags||[]).slice(0,3).map((t:string)=><span key={t} className="text-[9px] px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-600">{t}</span>)}</div></div></div>)}</div>;})()}
      </div>}
    </div>
  </div>);
}
