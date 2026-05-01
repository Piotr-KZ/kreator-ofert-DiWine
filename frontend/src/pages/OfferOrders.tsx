import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = '/api/v1/offers';
const CATS = [{id:'wine',label:'Wina'},{id:'sweet',label:'Słodycze'},{id:'decoration',label:'Dodatki'},{id:'packaging',label:'Opakowania'}];

interface OItem { id:string; name:string; category:string; base_price:number; quantity:number; }

export default function OfferOrders(){
  const nav=useNavigate();
  const [sups,setSups]=useState<any[]>([]);const [prods,setProds]=useState<any[]>([]);const [pkgs,setPkgs]=useState<any[]>([]);
  const [co,setCo]=useState<any>({});const [loading,setLoading]=useState(true);
  const [creating,setCreating]=useState(false);const [preview,setPreview]=useState(false);
  const [supId,setSupId]=useState('');const [cat,setCat]=useState('wine');
  const [items,setItems]=useState<OItem[]>([]);const [delDate,setDelDate]=useState('');const [payDate,setPayDate]=useState('');
  const printRef=useRef<HTMLDivElement>(null);

  useEffect(()=>{setLoading(true);Promise.all([
    axios.get(`${API}/catalog/suppliers`).catch(()=>({data:[]})),
    axios.get(`${API}/catalog/products`).catch(()=>({data:[]})),
    axios.get(`${API}/catalog/packagings`).catch(()=>({data:[]})),
    axios.get(`${API}/company-settings`).catch(()=>({data:{}})),
  ]).then(([s,p,pk,cs])=>{setSups(s.data);setProds(p.data);setPkgs(pk.data);setCo(cs.data);}).finally(()=>setLoading(false));},[]);

  const catItems=cat==='packaging'?pkgs.map(p=>({id:p.id,name:p.name,category:'packaging',base_price:p.price})):prods.filter(p=>p.category===cat).map(p=>({id:p.id,name:p.name,category:p.category,base_price:p.base_price}));
  const setQty=(id:string,qty:number)=>{setItems(prev=>{if(qty<=0)return prev.filter(i=>i.id!==id);const ex=prev.find(i=>i.id===id);if(ex)return prev.map(i=>i.id===id?{...i,quantity:qty}:i);const it=catItems.find(i=>i.id===id);return it?[...prev,{...it,quantity:qty}]:prev;});};
  const getQty=(id:string)=>items.find(i=>i.id===id)?.quantity||0;
  const total=items.reduce((s,i)=>s+i.base_price*i.quantity,0);
  const sup=sups.find(s=>s.id===supId);
  const today=new Date().toLocaleDateString('pl-PL');
  const orderNum=`ZAM/${new Date().getFullYear()}/${String(new Date().getMonth()+1).padStart(2,'0')}/${String(Math.floor(Math.random()*9000)+1000)}`;

  const handlePrint=()=>{if(!printRef.current)return;const w=window.open('','','width=800,height=600');if(!w)return;w.document.write('<html><head><title>Zamówienie</title></head><body>');w.document.write(printRef.current.innerHTML);w.document.write('</body></html>');w.document.close();w.print();};

  if(loading)return <div className="p-8 text-gray-400">Ładowanie...</div>;

  return(<div className="min-h-screen bg-gray-50" style={{fontFamily:"'Outfit',system-ui"}}>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet"/>
    <nav className="bg-gray-950 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3"><button onClick={()=>nav('/offer')} className="flex items-center gap-3"><div className="w-7 h-7 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600"/><span className="text-white font-bold">DiWine</span></button><span className="text-gray-600 text-sm">/ Zamówienia</span></div>
      <div className="flex items-center gap-1">
        <button onClick={()=>nav('/offer/list')} className="px-4 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg">Oferty</button>
        <button className="px-4 py-1.5 text-sm text-white bg-white/10 rounded-lg">Zamówienia</button>
        <button onClick={()=>nav('/offer/settings')} className="px-4 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg">Ustawienia</button>
      </div>
    </nav>

    <div className="max-w-5xl mx-auto px-6 py-6">
      {!creating&&!preview&&<div>
        <div className="flex items-center justify-between mb-6"><h2 className="text-xl font-bold text-gray-900">Zamówienia do dostawców</h2>
          <button onClick={()=>{setCreating(true);setSupId('');setItems([]);setDelDate('');setPayDate('');}} className="px-5 py-2 text-sm font-bold bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">+ Nowe zamówienie</button></div>
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">Brak zamówień. Kliknij "Nowe zamówienie".</div>
      </div>}

      {creating&&!preview&&<div>
        <div className="flex items-center justify-between mb-6"><h2 className="text-xl font-bold text-gray-900">Nowe zamówienie</h2>
          <button onClick={()=>setCreating(false)} className="text-sm text-gray-500">Anuluj</button></div>

        {/* Dostawca */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
          <div className="text-xs font-bold text-gray-500 mb-3">DOSTAWCA</div>
          <div className="flex gap-2">{sups.map(s=><button key={s.id} onClick={()=>setSupId(s.id)} className={`flex-1 p-3 rounded-lg border text-left text-sm ${supId===s.id?'border-indigo-400 bg-indigo-50':'border-gray-200 hover:border-gray-300'}`}><div className="font-bold">{s.name}</div><div className="text-xs text-gray-400">{s.contact_email} • {s.delivery_days} dni</div></button>)}</div>
        </div>

        {supId&&<>
          {/* Kategoria */}
          <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
            <div className="text-xs font-bold text-gray-500 mb-3">KATEGORIA</div>
            <div className="flex gap-2">{CATS.map(c=><button key={c.id} onClick={()=>setCat(c.id)} className={`px-4 py-2 rounded-lg text-sm font-semibold ${cat===c.id?'bg-indigo-600 text-white':'bg-gray-100 text-gray-600'}`}>{c.label}</button>)}</div>
          </div>

          {/* Pozycje */}
          <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
            <div className="text-xs font-bold text-gray-500 mb-3">POZYCJE — {CATS.find(c=>c.id===cat)?.label}</div>
            <div className="space-y-1">{catItems.map(item=>{const q=getQty(item.id);return(
              <div key={item.id} className={`flex items-center gap-3 px-3 py-2.5 rounded-lg border ${q>0?'border-indigo-200 bg-indigo-50/50':'border-gray-200'}`}>
                <span className="text-sm font-medium flex-1">{item.name}</span>
                <span className="text-sm text-gray-500 w-20 text-right">{item.base_price.toFixed(2)} zł</span>
                <div className="flex items-center gap-1">
                  <button onClick={()=>setQty(item.id,Math.max(0,q-10))} className="w-7 h-7 rounded border border-gray-200 text-gray-400 text-xs">-</button>
                  <input type="number" value={q||''} onChange={e=>setQty(item.id,parseInt(e.target.value)||0)} className="w-16 px-2 py-1 border border-gray-200 rounded text-sm text-center outline-none focus:border-indigo-400" placeholder="0"/>
                  <button onClick={()=>setQty(item.id,q+10)} className="w-7 h-7 rounded border border-gray-200 text-gray-400 text-xs">+</button>
                </div>
                <span className={`text-sm font-bold w-24 text-right ${q>0?'text-indigo-700':'text-gray-300'}`}>{q>0?`${(item.base_price*q).toFixed(2)} zł`:'—'}</span>
              </div>);})}</div>
          </div>

          {/* Terminy */}
          <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
            <div className="text-xs font-bold text-gray-500 mb-3">TERMINY</div>
            <div className="grid grid-cols-2 gap-3">
              <div><label className="text-[10px] text-gray-400 block mb-0.5">Termin dostawy</label><input type="date" className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={delDate} onChange={e=>setDelDate(e.target.value)}/></div>
              <div><label className="text-[10px] text-gray-400 block mb-0.5">Termin płatności</label><input type="date" className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400" value={payDate} onChange={e=>setPayDate(e.target.value)}/></div>
            </div>
          </div>

          {items.length>0&&<div className="flex items-center justify-between bg-indigo-50 rounded-xl p-4 mb-4">
            <span className="text-sm font-bold text-gray-700">Wartość zamówienia: <span className="text-indigo-700 text-lg">{total.toFixed(2)} zł netto</span></span>
            <button onClick={()=>setPreview(true)} className="px-6 py-2.5 text-sm font-bold bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Podgląd zamówienia</button>
          </div>}
        </>}
      </div>}

      {/* PODGLĄD / WYDRUK */}
      {preview&&<div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Podgląd zamówienia</h2>
          <div className="flex gap-2">
            <button onClick={()=>setPreview(false)} className="px-4 py-2 text-sm text-gray-500 border border-gray-200 rounded-lg">← Edytuj</button>
            <button onClick={handlePrint} className="px-4 py-2 text-sm font-bold bg-gray-900 text-white rounded-lg">Drukuj / PDF</button>
          </div>
        </div>

        {/* Szablon zamówienia */}
        <div ref={printRef}>
          <div style={{fontFamily:'Helvetica, Arial, sans-serif',fontSize:14,color:'#1F2937',maxWidth:720,margin:'0 auto',padding:32}}>

            {/* Nagłówek: DiWine + Dostawca */}
            <div style={{display:'flex',justifyContent:'space-between',marginBottom:32,paddingBottom:16,borderBottom:'2px solid #4F46E5'}}>
              <div>
                {co.logo_url&&<img src={co.logo_url} alt="" style={{height:40,marginBottom:8}}/>}
                <div style={{fontWeight:700,fontSize:16}}>{co.name} {co.legal_form}</div>
                {co.nip&&<div style={{fontSize:12,color:'#6B7280'}}>NIP: {co.nip}</div>}
                <div style={{fontSize:12,color:'#6B7280'}}>{[co.reg_street,co.reg_number].filter(Boolean).join(' ')}, {co.reg_postal} {co.reg_city}</div>
                {co.email&&<div style={{fontSize:12,color:'#6B7280'}}>{co.email}</div>}
              </div>
              <div style={{textAlign:'right'}}>
                <div style={{fontSize:12,color:'#6B7280'}}>Dostawca:</div>
                <div style={{fontWeight:700}}>{sup?.name}</div>
                {sup?.contact_email&&<div style={{fontSize:12,color:'#6B7280'}}>{sup.contact_email}</div>}
                {sup?.contact_phone&&<div style={{fontSize:12,color:'#6B7280'}}>{sup.contact_phone}</div>}
              </div>
            </div>

            {/* Tytuł */}
            <div style={{textAlign:'center',marginBottom:24}}>
              <div style={{fontSize:24,fontWeight:700,color:'#4F46E5'}}>ZAMÓWIENIE</div>
              <div style={{fontSize:12,color:'#6B7280'}}>Nr: {orderNum} • Data: {today}</div>
            </div>

            {/* Tabela pozycji */}
            <table style={{width:'100%',borderCollapse:'collapse',fontSize:13,marginBottom:24}}>
              <thead><tr style={{background:'#F9FAFB'}}>
                <th style={{textAlign:'left',padding:'8px 12px',borderBottom:'2px solid #E5E7EB',fontSize:11,color:'#6B7280'}}>Lp.</th>
                <th style={{textAlign:'left',padding:'8px 12px',borderBottom:'2px solid #E5E7EB',fontSize:11,color:'#6B7280'}}>Nazwa</th>
                <th style={{textAlign:'right',padding:'8px 12px',borderBottom:'2px solid #E5E7EB',fontSize:11,color:'#6B7280'}}>Cena jed.</th>
                <th style={{textAlign:'right',padding:'8px 12px',borderBottom:'2px solid #E5E7EB',fontSize:11,color:'#6B7280'}}>Ilość</th>
                <th style={{textAlign:'right',padding:'8px 12px',borderBottom:'2px solid #E5E7EB',fontSize:11,color:'#6B7280'}}>Wartość</th>
              </tr></thead>
              <tbody>{items.map((it,i)=>(
                <tr key={it.id}><td style={{padding:'8px 12px',borderBottom:'1px solid #E5E7EB'}}>{i+1}</td><td style={{padding:'8px 12px',borderBottom:'1px solid #E5E7EB',fontWeight:500}}>{it.name}</td><td style={{padding:'8px 12px',borderBottom:'1px solid #E5E7EB',textAlign:'right'}}>{it.base_price.toFixed(2)} zł</td><td style={{padding:'8px 12px',borderBottom:'1px solid #E5E7EB',textAlign:'right'}}>{it.quantity} szt.</td><td style={{padding:'8px 12px',borderBottom:'1px solid #E5E7EB',textAlign:'right',fontWeight:600}}>{(it.base_price*it.quantity).toFixed(2)} zł</td></tr>
              ))}</tbody>
              <tfoot><tr style={{background:'#EEF2FF'}}>
                <td colSpan={4} style={{padding:'10px 12px',fontWeight:700}}>RAZEM</td>
                <td style={{padding:'10px 12px',textAlign:'right',fontWeight:700,fontSize:16,color:'#4F46E5'}}>{total.toFixed(2)} zł netto</td>
              </tr></tfoot>
            </table>

            {/* Terminy */}
            <div style={{display:'flex',gap:32,marginBottom:32,fontSize:13}}>
              {delDate&&<div><span style={{color:'#6B7280'}}>Termin dostawy:</span> <strong>{delDate}</strong></div>}
              {payDate&&<div><span style={{color:'#6B7280'}}>Termin płatności:</span> <strong>{payDate}</strong></div>}
            </div>

            {/* Podpis */}
            <div style={{display:'flex',justifyContent:'space-between',marginTop:48,paddingTop:16,borderTop:'1px solid #E5E7EB'}}>
              <div style={{textAlign:'center',width:200}}>
                <div style={{borderTop:'1px solid #9CA3AF',marginTop:60,paddingTop:8,fontSize:11,color:'#6B7280'}}>
                  {co.person_first_name} {co.person_last_name}<br/>
                  {co.person_role||'Osoba zamawiająca'}<br/>
                  {co.person_phone}
                </div>
              </div>
              <div style={{textAlign:'center',width:200}}>
                <div style={{borderTop:'1px solid #9CA3AF',marginTop:60,paddingTop:8,fontSize:11,color:'#6B7280'}}>
                  Data i podpis dostawcy
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>}
    </div>
  </div>);
}
