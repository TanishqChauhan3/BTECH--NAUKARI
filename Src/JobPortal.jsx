import { useState, useEffect, useCallback, useRef } from "react";

const JOBS = [
  { id:1, title:"Software Engineer - Backend", company:"Google India", location:"Bangalore", type:"Private", experience:"0-2 yrs", salary:"₹18-28 LPA", posted:"2025-05-24", source:"LinkedIn", tags:["Python","Go","Distributed Systems"], logo:"G", color:"#4285F4", featured:true },
  { id:2, title:"Junior Developer (NIC Empanelled)", company:"National Informatics Centre", location:"Delhi", type:"Govt", experience:"0-1 yrs", salary:"₹6-8 LPA", posted:"2025-05-23", source:"NIC Portal", tags:["Java","Spring Boot","Oracle"], logo:"N", color:"#1a5276", featured:false },
  { id:3, title:"SDE-1 (Full Stack)", company:"Flipkart", location:"Bangalore", type:"Private", experience:"0-2 yrs", salary:"₹22-32 LPA", posted:"2025-05-24", source:"Instahyre", tags:["React","Node.js","MongoDB"], logo:"F", color:"#F7941D", featured:true },
  { id:4, title:"Management Trainee (IT)", company:"Bharat Electronics Limited", location:"Hyderabad", type:"PSU", experience:"Fresher", salary:"₹6.5 LPA CTC", posted:"2025-05-22", source:"BEL Portal", tags:["C++","Embedded","Linux"], logo:"B", color:"#1a7431", featured:false },
  { id:5, title:"Associate Software Engineer", company:"Accenture", location:"Pune", type:"Private", experience:"0-1 yrs", salary:"₹4.5-6 LPA", posted:"2025-05-23", source:"Naukri", tags:["Java","SQL","REST APIs"], logo:"A", color:"#A100FF", featured:false },
  { id:6, title:"Technical Officer Grade-B", company:"DRDO", location:"Delhi", type:"Govt", experience:"Fresher", salary:"₹9-15 LPA", posted:"2025-05-21", source:"DRDO Portal", tags:["C","MATLAB","Signal Processing"], logo:"D", color:"#8B0000", featured:false },
  { id:7, title:"Frontend Engineer", company:"Zepto", location:"Mumbai", type:"Private", experience:"0-2 yrs", salary:"₹15-25 LPA", posted:"2025-05-24", source:"LinkedIn", tags:["React","TypeScript","Redux"], logo:"Z", color:"#7C3AED", featured:true },
  { id:8, title:"Executive Engineer (IT)", company:"ONGC", location:"Dehradun", type:"PSU", experience:"Fresher", salary:"₹8.4 LPA", posted:"2025-05-20", source:"ONGC Portal", tags:["SAP","ERP","Networking"], logo:"O", color:"#D97706", featured:false },
  { id:9, title:"Systems Engineer", company:"TCS", location:"Chennai", type:"Private", experience:"0-1 yrs", salary:"₹3.5-4.5 LPA", posted:"2025-05-23", source:"TCS iBegin", tags:["Java","Python","SQL"], logo:"T", color:"#0066CC", featured:false },
  { id:10, title:"Programmer (SSC CHSL IT)", company:"Staff Selection Commission", location:"Pan India", type:"Govt", experience:"Fresher", salary:"₹5.2-7.5 LPA", posted:"2025-05-22", source:"SSC Portal", tags:["Networking","Windows Server","Troubleshooting"], logo:"S", color:"#155724", featured:false },
  { id:11, title:"Software Dev Engineer", company:"Amazon India", location:"Hyderabad", type:"Private", experience:"0-2 yrs", salary:"₹25-40 LPA", posted:"2025-05-24", source:"Amazon Jobs", tags:["Java","AWS","Data Structures"], logo:"A", color:"#FF9900", featured:true },
  { id:12, title:"Junior Engineer (IT)", company:"NTPC Limited", location:"Noida", type:"PSU", experience:"Fresher", salary:"₹7.5 LPA", posted:"2025-05-21", source:"NTPC Portal", tags:["Networking","SAP","ERP"], logo:"N", color:"#004080", featured:false },
  { id:13, title:"Graduate Engineer Trainee", company:"Infosys", location:"Mysore", type:"Private", experience:"Fresher", salary:"₹3.6-4.5 LPA", posted:"2025-05-20", source:"Infosys Careers", tags:["Java","Python","Agile"], logo:"I", color:"#007CC3", featured:false },
  { id:14, title:"Scientist-B (CS)", company:"ISRO", location:"Bangalore", type:"Govt", experience:"Fresher", salary:"₹56,100/mo", posted:"2025-05-19", source:"ISRO Portal", tags:["C","Embedded","Real-Time OS"], logo:"I", color:"#1a2a6c", featured:true },
  { id:15, title:"Backend Engineer (Intern→FTE)", company:"Razorpay", location:"Bangalore", type:"Private", experience:"0-1 yrs", salary:"₹12-20 LPA", posted:"2025-05-24", source:"Wellfound", tags:["Go","Microservices","PostgreSQL"], logo:"R", color:"#072654", featured:false },
  { id:16, title:"Junior Engineer (CS)", company:"Coal India Limited", company:"GAIL India", location:"Noida", type:"PSU", experience:"Fresher", salary:"₹7 LPA", posted:"2025-05-22", source:"GAIL Portal", tags:["SAP","IT Infrastructure","Networking"], logo:"G", color:"#c0392b", featured:false },
  { id:17, title:"Software Developer", company:"Zomato", location:"Gurugram", type:"Private", experience:"0-2 yrs", salary:"₹18-30 LPA", posted:"2025-05-23", source:"LinkedIn", tags:["Python","Kafka","Redis"], logo:"Z", color:"#E23744", featured:false },
  { id:18, title:"Junior Telecom Officer (IT)", company:"BSNL", location:"Pan India", type:"Govt", experience:"Fresher", salary:"₹40,000/mo", posted:"2025-05-18", source:"BSNL Portal", tags:["Linux","Networking","CCNA"], logo:"B", color:"#003580", featured:false },
];

const LOCATIONS = ["All Locations","Bangalore","Delhi","Mumbai","Hyderabad","Pune","Chennai","Noida","Gurugram","Mysore","Dehradun","Pan India"];
const EXPERIENCE = ["All Levels","Fresher","0-1 yrs","0-2 yrs"];
const TYPES = ["All","Private","Govt","PSU"];

const STATS = [
  { label:"Total Listings", value:"18,400+", icon:"📋" },
  { label:"Private Sector", value:"11,200+", icon:"🏢" },
  { label:"Government", value:"4,800+", icon:"🏛️" },
  { label:"PSU Openings", value:"2,400+", icon:"🔧" },
];

function timeAgo(dateStr) {
  const diff = Math.floor((new Date() - new Date(dateStr)) / 86400000);
  if (diff === 0) return "Today";
  if (diff === 1) return "Yesterday";
  return `${diff}d ago`;
}

function Badge({ type }) {
  const cfg = {
    Private: { bg:"#EFF6FF", color:"#1D4ED8", border:"#BFDBFE" },
    Govt:    { bg:"#F0FDF4", color:"#166534", border:"#BBF7D0" },
    PSU:     { bg:"#FFFBEB", color:"#92400E", border:"#FDE68A" },
  }[type] || {};
  return (
    <span style={{ fontSize:11, fontWeight:600, padding:"2px 8px", borderRadius:20, background:cfg.bg, color:cfg.color, border:`1px solid ${cfg.border}`, letterSpacing:"0.03em", fontFamily:"'DM Mono', monospace" }}>
      {type}
    </span>
  );
}

function JobCard({ job, onClick }) {
  const [hov, setHov] = useState(false);
  return (
    <div
      onClick={() => onClick(job)}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        background: hov ? "#fff" : "#FAFAF9",
        border: `1.5px solid ${hov ? job.color : "#E7E5E0"}`,
        borderRadius: 16,
        padding: "22px 24px",
        cursor: "pointer",
        transition: "all 0.18s ease",
        transform: hov ? "translateY(-2px)" : "none",
        boxShadow: hov ? `0 8px 32px ${job.color}22` : "0 1px 4px rgba(0,0,0,0.04)",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {job.featured && (
        <div style={{ position:"absolute", top:0, right:0, background:job.color, color:"#fff", fontSize:10, fontWeight:700, padding:"3px 12px", borderBottomLeftRadius:10, letterSpacing:"0.08em", fontFamily:"'DM Mono', monospace" }}>
          FEATURED
        </div>
      )}
      <div style={{ display:"flex", gap:14, alignItems:"flex-start" }}>
        <div style={{ width:46, height:46, borderRadius:12, background:job.color, display:"flex", alignItems:"center", justifyContent:"center", color:"#fff", fontWeight:800, fontSize:18, flexShrink:0, fontFamily:"'Playfair Display', serif", boxShadow:`0 4px 12px ${job.color}44` }}>
          {job.logo}
        </div>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:2, flexWrap:"wrap" }}>
            <h3 style={{ margin:0, fontSize:15, fontWeight:700, color:"#1C1917", fontFamily:"'Playfair Display', serif", lineHeight:1.3 }}>{job.title}</h3>
          </div>
          <div style={{ fontSize:13, color:"#57534E", marginBottom:8, fontWeight:500 }}>{job.company}</div>
          <div style={{ display:"flex", gap:12, flexWrap:"wrap", marginBottom:10 }}>
            <span style={{ fontSize:12, color:"#78716C", display:"flex", alignItems:"center", gap:4 }}>📍 {job.location}</span>
            <span style={{ fontSize:12, color:"#78716C", display:"flex", alignItems:"center", gap:4 }}>💼 {job.experience}</span>
            <span style={{ fontSize:12, color:"#059669", fontWeight:600 }}>💰 {job.salary}</span>
          </div>
          <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", flexWrap:"wrap", gap:8 }}>
            <div style={{ display:"flex", gap:6, flexWrap:"wrap" }}>
              {job.tags.slice(0,3).map(t => (
                <span key={t} style={{ fontSize:11, padding:"2px 8px", borderRadius:6, background:"#F5F5F4", color:"#57534E", fontFamily:"'DM Mono', monospace", border:"1px solid #E7E5E0" }}>{t}</span>
              ))}
            </div>
            <div style={{ display:"flex", gap:8, alignItems:"center" }}>
              <Badge type={job.type} />
              <span style={{ fontSize:11, color:"#A8A29E" }}>{timeAgo(job.posted)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Modal({ job, onClose }) {
  useEffect(() => {
    const handler = e => { if(e.key==="Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  if (!job) return null;
  return (
    <div onClick={onClose} style={{ position:"fixed", inset:0, background:"rgba(0,0,0,0.55)", zIndex:1000, display:"flex", alignItems:"center", justifyContent:"center", padding:20, backdropFilter:"blur(4px)" }}>
      <div onClick={e => e.stopPropagation()} style={{ background:"#fff", borderRadius:20, width:"100%", maxWidth:620, maxHeight:"85vh", overflowY:"auto", padding:36, position:"relative", boxShadow:"0 24px 80px rgba(0,0,0,0.2)" }}>
        <button onClick={onClose} style={{ position:"absolute", top:16, right:16, background:"#F5F5F4", border:"none", borderRadius:8, width:32, height:32, cursor:"pointer", fontSize:16, display:"flex", alignItems:"center", justifyContent:"center" }}>✕</button>
        <div style={{ display:"flex", gap:18, alignItems:"center", marginBottom:24 }}>
          <div style={{ width:64, height:64, borderRadius:16, background:job.color, display:"flex", alignItems:"center", justifyContent:"center", color:"#fff", fontWeight:900, fontSize:26, flexShrink:0, fontFamily:"'Playfair Display', serif", boxShadow:`0 6px 20px ${job.color}55` }}>{job.logo}</div>
          <div>
            <h2 style={{ margin:"0 0 4px", fontSize:20, fontWeight:800, color:"#1C1917", fontFamily:"'Playfair Display', serif" }}>{job.title}</h2>
            <div style={{ fontSize:14, color:"#57534E", fontWeight:600 }}>{job.company}</div>
          </div>
        </div>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:14, marginBottom:24 }}>
          {[["📍 Location", job.location],["💼 Experience", job.experience],["💰 Salary", job.salary],["🏷️ Type", job.type],["🗓️ Posted", job.posted],["🔗 Source", job.source]].map(([l,v])=>(
            <div key={l} style={{ background:"#FAFAF9", borderRadius:10, padding:"12px 16px", border:"1px solid #E7E5E0" }}>
              <div style={{ fontSize:11, color:"#A8A29E", marginBottom:4, fontFamily:"'DM Mono', monospace" }}>{l}</div>
              <div style={{ fontSize:13, fontWeight:600, color:"#292524" }}>{v}</div>
            </div>
          ))}
        </div>
        <div style={{ marginBottom:20 }}>
          <div style={{ fontSize:12, color:"#A8A29E", marginBottom:8, fontFamily:"'DM Mono', monospace", letterSpacing:"0.06em" }}>SKILLS REQUIRED</div>
          <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
            {job.tags.map(t => (
              <span key={t} style={{ fontSize:12, padding:"4px 12px", borderRadius:8, background:job.color+"18", color:job.color, fontFamily:"'DM Mono', monospace", border:`1px solid ${job.color}33`, fontWeight:600 }}>{t}</span>
            ))}
          </div>
        </div>
        <div style={{ marginBottom:24, padding:18, background:"#F9F9F8", borderRadius:12, border:"1px solid #E7E5E0" }}>
          <div style={{ fontSize:12, color:"#A8A29E", marginBottom:8, fontFamily:"'DM Mono', monospace", letterSpacing:"0.06em" }}>ABOUT THE ROLE</div>
          <p style={{ margin:0, fontSize:13, color:"#57534E", lineHeight:1.7 }}>
            This is an excellent opportunity for B.Tech Computer Science graduates to kickstart their career at {job.company}. You will work with a dynamic team on cutting-edge technology, contributing to real-world projects from day one. The role involves hands-on development, code reviews, and close collaboration with senior engineers.
          </p>
        </div>
        <a href="#apply" onClick={e=>e.preventDefault()} style={{ display:"block", textAlign:"center", padding:"14px 32px", background:job.color, color:"#fff", borderRadius:12, fontWeight:700, fontSize:15, textDecoration:"none", letterSpacing:"0.01em", boxShadow:`0 6px 20px ${job.color}44`, transition:"opacity 0.15s" }}
          onMouseEnter={e=>e.target.style.opacity="0.9"} onMouseLeave={e=>e.target.style.opacity="1"}>
          Apply Now →
        </a>
      </div>
    </div>
  );
}

export default function App() {
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("All");
  const [locFilter, setLocFilter] = useState("All Locations");
  const [expFilter, setExpFilter] = useState("All Levels");
  const [selectedJob, setSelectedJob] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [page, setPage] = useState(1);
  const PER_PAGE = 9;

  const filtered = JOBS.filter(j => {
    const q = search.toLowerCase();
    const matchQ = !q || j.title.toLowerCase().includes(q) || j.company.toLowerCase().includes(q) || j.tags.some(t=>t.toLowerCase().includes(q)) || j.location.toLowerCase().includes(q);
    const matchT = typeFilter === "All" || j.type === typeFilter;
    const matchL = locFilter === "All Locations" || j.location.includes(locFilter.split(",")[0]);
    const matchE = expFilter === "All Levels" || j.experience === expFilter;
    return matchQ && matchT && matchL && matchE;
  });

  const paginated = filtered.slice(0, page * PER_PAGE);
  const hasMore = paginated.length < filtered.length;

  const clearFilters = () => { setSearch(""); setTypeFilter("All"); setLocFilter("All Locations"); setExpFilter("All Levels"); setPage(1); };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');
        * { box-sizing: border-box; }
        body { margin:0; background:#F5F5F0; font-family:'DM Sans',sans-serif; }
        ::-webkit-scrollbar { width:6px; }
        ::-webkit-scrollbar-track { background:#F5F5F0; }
        ::-webkit-scrollbar-thumb { background:#D6D3D1; border-radius:10px; }
        input,select { outline:none; }
        @keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
        .card-appear { animation: fadeUp 0.3s ease both; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
        .live-dot { animation: pulse 2s infinite; }
      `}</style>

      {/* HEADER */}
      <header style={{ background:"#1C1917", position:"sticky", top:0, zIndex:200 }}>
        <div style={{ maxWidth:1200, margin:"0 auto", padding:"0 24px", height:64, display:"flex", alignItems:"center", gap:20, justifyContent:"space-between" }}>
          <div style={{ display:"flex", alignItems:"center", gap:12 }}>
            <div style={{ width:36, height:36, borderRadius:10, background:"linear-gradient(135deg,#F59E0B,#EF4444)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:18 }}>🎓</div>
            <div>
              <div style={{ fontFamily:"'Playfair Display', serif", fontWeight:900, fontSize:18, color:"#FAFAF9", letterSpacing:"-0.02em", lineHeight:1 }}>CareerBridge</div>
              <div style={{ fontSize:10, color:"#78716C", fontFamily:"'DM Mono', monospace", letterSpacing:"0.08em" }}>B.TECH CS JOBS</div>
            </div>
          </div>
          <div style={{ flex:1, maxWidth:480, position:"relative" }}>
            <span style={{ position:"absolute", left:14, top:"50%", transform:"translateY(-50%)", fontSize:16 }}>🔍</span>
            <input
              value={search}
              onChange={e=>{setSearch(e.target.value);setPage(1);}}
              placeholder="Search by title, company, or skill..."
              style={{ width:"100%", padding:"10px 16px 10px 40px", borderRadius:12, border:"1.5px solid #44403C", background:"#292524", color:"#FAFAF9", fontSize:14, fontFamily:"'DM Sans', sans-serif", transition:"border-color 0.15s" }}
              onFocus={e=>e.target.style.borderColor="#F59E0B"}
              onBlur={e=>e.target.style.borderColor="#44403C"}
            />
          </div>
          <div style={{ display:"flex", alignItems:"center", gap:10 }}>
            <span className="live-dot" style={{ width:8, height:8, borderRadius:"50%", background:"#22C55E", display:"inline-block" }}></span>
            <span style={{ fontSize:12, color:"#78716C", fontFamily:"'DM Mono', monospace" }}>LIVE</span>
            <button onClick={()=>setSidebarOpen(s=>!s)} style={{ display:"none", background:"#292524", border:"none", color:"#FAFAF9", padding:"8px 12px", borderRadius:8, cursor:"pointer", fontSize:13 }} className="mob-menu">☰ Filters</button>
          </div>
        </div>
      </header>

      {/* STATS BANNER */}
      <div style={{ background:"#292524", borderBottom:"1px solid #44403C" }}>
        <div style={{ maxWidth:1200, margin:"0 auto", padding:"12px 24px", display:"flex", gap:32, flexWrap:"wrap", justifyContent:"center" }}>
          {STATS.map(s=>(
            <div key={s.label} style={{ display:"flex", alignItems:"center", gap:8 }}>
              <span style={{ fontSize:16 }}>{s.icon}</span>
              <span style={{ fontFamily:"'Playfair Display', serif", fontWeight:700, fontSize:16, color:"#F59E0B" }}>{s.value}</span>
              <span style={{ fontSize:12, color:"#78716C" }}>{s.label}</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ maxWidth:1200, margin:"0 auto", padding:"28px 24px", display:"flex", gap:24, alignItems:"flex-start" }}>
        {/* SIDEBAR */}
        <aside style={{ width:240, flexShrink:0, position:"sticky", top:80 }}>
          <div style={{ background:"#fff", borderRadius:16, padding:20, border:"1.5px solid #E7E5E0", boxShadow:"0 2px 12px rgba(0,0,0,0.04)" }}>
            <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:20 }}>
              <span style={{ fontSize:13, fontWeight:700, color:"#1C1917", fontFamily:"'DM Mono', monospace", letterSpacing:"0.04em" }}>FILTERS</span>
              <button onClick={clearFilters} style={{ fontSize:11, color:"#F59E0B", background:"none", border:"none", cursor:"pointer", fontWeight:600, padding:0 }}>Clear all</button>
            </div>

            {/* Type filter */}
            <div style={{ marginBottom:20 }}>
              <div style={{ fontSize:11, color:"#A8A29E", marginBottom:10, fontFamily:"'DM Mono', monospace", letterSpacing:"0.06em" }}>JOB CATEGORY</div>
              <div style={{ display:"flex", flexDirection:"column", gap:6 }}>
                {TYPES.map(t => (
                  <button key={t} onClick={()=>{setTypeFilter(t);setPage(1);}} style={{ textAlign:"left", padding:"8px 12px", borderRadius:8, border:`1.5px solid ${typeFilter===t?"#F59E0B":"#E7E5E0"}`, background:typeFilter===t?"#FFFBEB":"transparent", color:typeFilter===t?"#92400E":"#57534E", fontSize:13, fontWeight:typeFilter===t?600:400, cursor:"pointer", transition:"all 0.15s", display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                    {t === "All" ? "🌐 All Jobs" : t === "Private" ? "🏢 Private" : t === "Govt" ? "🏛️ Government" : "🔧 PSU"}
                    <span style={{ fontSize:11, background:"#F5F5F4", borderRadius:4, padding:"1px 6px", color:"#A8A29E", fontFamily:"'DM Mono', monospace" }}>{JOBS.filter(j=>t==="All"||j.type===t).length}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Location filter */}
            <div style={{ marginBottom:20 }}>
              <div style={{ fontSize:11, color:"#A8A29E", marginBottom:8, fontFamily:"'DM Mono', monospace", letterSpacing:"0.06em" }}>LOCATION</div>
              <select value={locFilter} onChange={e=>{setLocFilter(e.target.value);setPage(1);}} style={{ width:"100%", padding:"9px 12px", borderRadius:8, border:"1.5px solid #E7E5E0", background:"#FAFAF9", color:"#292524", fontSize:13, fontFamily:"'DM Sans',sans-serif", cursor:"pointer" }}>
                {LOCATIONS.map(l=><option key={l}>{l}</option>)}
              </select>
            </div>

            {/* Experience filter */}
            <div>
              <div style={{ fontSize:11, color:"#A8A29E", marginBottom:8, fontFamily:"'DM Mono', monospace", letterSpacing:"0.06em" }}>EXPERIENCE</div>
              <div style={{ display:"flex", flexDirection:"column", gap:6 }}>
                {EXPERIENCE.map(e => (
                  <button key={e} onClick={()=>{setExpFilter(e);setPage(1);}} style={{ textAlign:"left", padding:"8px 12px", borderRadius:8, border:`1.5px solid ${expFilter===e?"#10B981":"#E7E5E0"}`, background:expFilter===e?"#ECFDF5":"transparent", color:expFilter===e?"#065F46":"#57534E", fontSize:13, fontWeight:expFilter===e?600:400, cursor:"pointer", transition:"all 0.15s" }}>
                    {e}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Source legend */}
          <div style={{ background:"#fff", borderRadius:16, padding:18, border:"1.5px solid #E7E5E0", marginTop:16, boxShadow:"0 2px 12px rgba(0,0,0,0.04)" }}>
            <div style={{ fontSize:11, color:"#A8A29E", marginBottom:12, fontFamily:"'DM Mono', monospace", letterSpacing:"0.06em" }}>DATA SOURCES</div>
            {["LinkedIn","Naukri","NIC Portal","SSC Portal","BEL Portal","Internshala"].map(s=>(
              <div key={s} style={{ display:"flex", alignItems:"center", gap:8, marginBottom:8 }}>
                <span className="live-dot" style={{ width:6, height:6, borderRadius:"50%", background:"#22C55E", flexShrink:0 }}></span>
                <span style={{ fontSize:12, color:"#57534E" }}>{s}</span>
              </div>
            ))}
            <div style={{ fontSize:11, color:"#A8A29E", marginTop:4, fontFamily:"'DM Mono', monospace" }}>+12 more active</div>
          </div>
        </aside>

        {/* MAIN CONTENT */}
        <main style={{ flex:1, minWidth:0 }}>
          {/* Results header */}
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:20, flexWrap:"wrap", gap:12 }}>
            <div>
              <span style={{ fontSize:22, fontWeight:800, color:"#1C1917", fontFamily:"'Playfair Display', serif" }}>{filtered.length} </span>
              <span style={{ fontSize:16, color:"#78716C" }}>jobs found</span>
              {search && <span style={{ fontSize:14, color:"#A8A29E" }}> for "<strong style={{color:"#1C1917"}}>{search}</strong>"</span>}
            </div>
            <div style={{ display:"flex", gap:8 }}>
              {[["All","All"],["Private","Private"],["Govt","Govt"],["PSU","PSU"]].map(([label,val])=>(
                <button key={val} onClick={()=>{setTypeFilter(val);setPage(1);}} style={{ padding:"6px 14px", borderRadius:20, border:`1.5px solid ${typeFilter===val?"#1C1917":"#E7E5E0"}`, background:typeFilter===val?"#1C1917":"transparent", color:typeFilter===val?"#FAFAF9":"#57534E", fontSize:12, fontWeight:600, cursor:"pointer", fontFamily:"'DM Mono', monospace", transition:"all 0.15s" }}>
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Featured strip */}
          {typeFilter === "All" && !search && page === 1 && (
            <div style={{ marginBottom:24, padding:18, background:"linear-gradient(135deg,#1C1917 0%,#292524 100%)", borderRadius:16, border:"1px solid #44403C" }}>
              <div style={{ fontSize:11, color:"#F59E0B", fontFamily:"'DM Mono', monospace", letterSpacing:"0.1em", marginBottom:12 }}>⭐ FEATURED OPPORTUNITIES</div>
              <div style={{ display:"flex", gap:10, overflowX:"auto", paddingBottom:4 }}>
                {JOBS.filter(j=>j.featured).map(j=>(
                  <div key={j.id} onClick={()=>setSelectedJob(j)} style={{ flexShrink:0, background:"#44403C", borderRadius:12, padding:"10px 16px", cursor:"pointer", border:`1.5px solid ${j.color}44`, minWidth:200, transition:"all 0.15s" }}
                    onMouseEnter={e=>{e.currentTarget.style.borderColor=j.color;e.currentTarget.style.background="#57534E";}}
                    onMouseLeave={e=>{e.currentTarget.style.borderColor=j.color+"44";e.currentTarget.style.background="#44403C";}}>
                    <div style={{ fontSize:12, fontWeight:700, color:"#FAFAF9", marginBottom:2 }}>{j.title}</div>
                    <div style={{ fontSize:11, color:"#A8A29E" }}>{j.company} · {j.location}</div>
                    <div style={{ fontSize:11, color:j.color, marginTop:4, fontWeight:600 }}>{j.salary}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Job grid */}
          {filtered.length === 0 ? (
            <div style={{ textAlign:"center", padding:"80px 20px", background:"#fff", borderRadius:16, border:"1.5px dashed #E7E5E0" }}>
              <div style={{ fontSize:48, marginBottom:12 }}>🔍</div>
              <div style={{ fontSize:18, fontWeight:700, color:"#1C1917", fontFamily:"'Playfair Display', serif", marginBottom:8 }}>No jobs found</div>
              <div style={{ fontSize:14, color:"#A8A29E", marginBottom:20 }}>Try adjusting your filters or search terms</div>
              <button onClick={clearFilters} style={{ padding:"10px 24px", background:"#1C1917", color:"#FAFAF9", border:"none", borderRadius:10, cursor:"pointer", fontSize:14, fontWeight:600 }}>Clear filters</button>
            </div>
          ) : (
            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(340px,1fr))", gap:16 }}>
              {paginated.map((job, i) => (
                <div key={job.id} className="card-appear" style={{ animationDelay:`${(i%PER_PAGE)*0.04}s` }}>
                  <JobCard job={job} onClick={setSelectedJob} />
                </div>
              ))}
            </div>
          )}

          {/* Load more */}
          {hasMore && (
            <div style={{ textAlign:"center", marginTop:28 }}>
              <button onClick={()=>setPage(p=>p+1)} style={{ padding:"12px 36px", background:"#1C1917", color:"#FAFAF9", border:"none", borderRadius:12, cursor:"pointer", fontSize:14, fontWeight:600, fontFamily:"'DM Sans', sans-serif", transition:"background 0.15s" }}
                onMouseEnter={e=>e.target.style.background="#292524"} onMouseLeave={e=>e.target.style.background="#1C1917"}>
                Load more jobs ({filtered.length - paginated.length} remaining)
              </button>
            </div>
          )}

          {/* Footer info */}
          <div style={{ marginTop:40, padding:20, background:"#fff", borderRadius:16, border:"1.5px solid #E7E5E0", display:"flex", gap:24, flexWrap:"wrap", justifyContent:"space-between" }}>
            <div>
              <div style={{ fontSize:13, fontWeight:700, color:"#1C1917", marginBottom:4 }}>🔄 Auto-refreshed every 30 min</div>
              <div style={{ fontSize:12, color:"#A8A29E" }}>Scrapers running across 18+ portals via RSS + Playwright</div>
            </div>
            <div>
              <div style={{ fontSize:13, fontWeight:700, color:"#1C1917", marginBottom:4 }}>🛡️ Verified sources only</div>
              <div style={{ fontSize:12, color:"#A8A29E" }}>All listings sourced from official company portals</div>
            </div>
            <div>
              <div style={{ fontSize:13, fontWeight:700, color:"#1C1917", marginBottom:4 }}>📧 Job alerts coming soon</div>
              <div style={{ fontSize:12, color:"#A8A29E" }}>Get notified for matching openings via email</div>
            </div>
          </div>
        </main>
      </div>

      {/* Modal */}
      <Modal job={selectedJob} onClose={()=>setSelectedJob(null)} />
    </>
  );
}
