import React, {useEffect, useState} from "react";
import {createRoot} from "react-dom/client";
import axios from "axios";
import {Line, Doughnut, Bar} from "react-chartjs-2";
import {Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend} from "chart.js";
import "./styles.css";
ChartJS.register(CategoryScale,LinearScale,PointElement,LineElement,BarElement,ArcElement,Tooltip,Legend);

const riskColors={low:"#35c759",moderate:"#ffca28",medium:"#ffca28",high:"#ff4545",critical:"#ff4545"};
const riskLabelsPlugin={id:"riskLabels",afterDatasetsDraw(chart){const dataset=chart.data.datasets[0];const total=dataset.data.reduce((sum,value)=>sum+Number(value),0);const meta=chart.getDatasetMeta(0);const context=chart.ctx;context.save();context.fillStyle="#ffffff";context.font="700 18px Inter, sans-serif";context.textAlign="center";context.textBaseline="middle";meta.data.forEach((arc,index)=>{const value=Number(dataset.data[index]);if(!value)return;const angle=(arc.startAngle+arc.endAngle)/2;const radius=(arc.innerRadius+arc.outerRadius)/2;const x=arc.x+Math.cos(angle)*radius;const y=arc.y+Math.sin(angle)*radius;context.fillText(`${Math.round(value/total*100)}%`,x,y)});context.restore()}};
const riskChartOptions={responsive:true,maintainAspectRatio:true,cutout:"54%",plugins:{legend:{position:"top",labels:{color:"#f4f7f1",font:{size:15,weight:"600"},padding:20,usePointStyle:false}},tooltip:{callbacks:{label(context){const total=context.dataset.data.reduce((sum,value)=>sum+Number(value),0);return ` ${context.label}: ${Math.round(Number(context.raw)/total*100)}%`}}}}};
const lineChartOptions={responsive:true,maintainAspectRatio:true,interaction:{mode:"index",intersect:false},plugins:{legend:{position:"top",labels:{color:"#245465",font:{size:15,weight:"600"},padding:20,usePointStyle:true}},tooltip:{mode:"index",intersect:false}},scales:{x:{ticks:{color:"#315866",font:{size:12}},grid:{color:"#6f9eaa55"}},y:{ticks:{color:"#315866",font:{size:12}},grid:{color:"#6f9eaa55"}}}};

const API="http://127.0.0.1:8000/api";
function api(){const t=localStorage.getItem("token"); return axios.create({baseURL:API,headers:t?{Authorization:`Bearer ${t}`}:{}})}
function Login({onLogin}){const [u,setU]=useState("admin"),[p,setP]=useState("PRJ666@Demo"),[err,setErr]=useState("");
async function go(e){e.preventDefault();try{const r=await axios.post(API+"/auth/login",{username:u,password:p});localStorage.setItem("token",r.data.access_token);onLogin()}catch(x){setErr(x.response?.data?.detail||"Login failed")}}
return <div className="login"><div className="login-card"><div className="brand">🌍 Climate Change</div><h1>Climate Change</h1><p>Climate Change Impact Assessment & Environmental Risk Prediction</p><form onSubmit={go}><input value={u} onChange={e=>setU(e.target.value)} placeholder="Username"/><input type="password" value={p} onChange={e=>setP(e.target.value)} placeholder="Password"/><button>Sign in</button></form><small>Demo: admin / PRJ666@Demo</small>{err&&<div className="error">{err}</div>}</div></div>}

function App(){
 const [dash,setDash]=useState(null),[analytics,setAnalytics]=useState(null),[tab,setTab]=useState("Dashboard"),[pred,setPred]=useState(null),[metrics,setMetrics]=useState(null),[data,setData]=useState([]),[alerts,setAlerts]=useState([]);
 const load=async()=>{try{const a=api(); const [d,x,m,e,al]=await Promise.all([a.get("/dashboard"),a.get("/analytics"),a.get("/model-metrics"),a.get("/environmental-data?limit=80"),a.get("/alerts")]);setDash(d.data);setAnalytics(x.data);setMetrics(m.data);setData(e.data.items);setAlerts(al.data.items)}catch(err){if(err.response?.status===401){localStorage.removeItem("token");location.reload()}}};
 useEffect(()=>{load()},[]);
 const logout=()=>{localStorage.removeItem("token");location.reload()};
 const riskClass=(r)=>String(r||"").toLowerCase();
 if(!dash)return <div className="loading">Loading climate intelligence…</div>;
 const monthly=analytics.monthly;
 const lineData={labels:monthly.slice(-18).map(x=>x.month),datasets:[
    {label:"Energy (kWh)",data:monthly.slice(-18).map(x=>x.energy_kwh),borderColor:"#18a94b",backgroundColor:"#18a94b",pointBackgroundColor:"#18a94b",pointBorderColor:"#ffffff",pointBorderWidth:3,pointRadius:6,pointHoverRadius:8,borderWidth:4,tension:.3},
    {label:"CO₂ (kg)",data:monthly.slice(-18).map(x=>x.co2_kg),borderColor:"#1769e8",backgroundColor:"#1769e8",pointBackgroundColor:"#1769e8",pointBorderColor:"#ffffff",pointBorderWidth:3,pointRadius:6,pointHoverRadius:8,borderWidth:4,tension:.3}
 ]};
 const riskData={labels:Object.keys(analytics.risk_counts),datasets:[{data:Object.values(analytics.risk_counts),backgroundColor:Object.keys(analytics.risk_counts).map(label=>riskColors[String(label).toLowerCase()]||"#8fd4e5"),borderColor:"#f4f7f1",borderWidth:3}]};
 const nav=["Dashboard","Climate Data","AI Prediction","Analytics","Alerts","Recommendations","About"];
 return <div className="app"><aside><div className="logo">🌍 <b>Climate Change</b></div><div className="sub">CLIMATE INTELLIGENCE</div>{nav.map(n=><button className={tab===n?"nav active":"nav"} onClick={()=>setTab(n)} key={n}>{n}</button>)}<button className="nav logout" onClick={logout}>Sign out</button></aside>
 <main><header><div><div className="eyebrow">CLIMATE CHANGE IMPACT ASSESSMENT</div><h2>{tab}</h2></div><div className="status">● Local data provider <span>Secure session</span></div></header>
 {tab==="Dashboard"&&<Dashboard dash={dash} analytics={analytics} lineData={lineData} riskData={riskData} riskClass={riskClass}/>}
 {tab==="Climate Data"&&<DataTable data={data}/>}
 {tab==="AI Prediction"&&<Prediction onResult={setPred} result={pred} metrics={metrics}/>}
 {tab==="Analytics"&&<Analytics analytics={analytics} lineData={lineData} riskData={riskData} metrics={metrics}/>}
 {tab==="Alerts"&&<Alerts alerts={alerts}/>}
 {tab==="Recommendations"&&<Recommendations items={dash.recommendations}/>}
 {tab==="About"&&<About/>}
 </main></div>
}

function Dashboard({dash,analytics,lineData,riskData,riskClass}){return <section>
<div className="hero"><div><span className="pill">SDG 13 • CLIMATE ACTION</span><h1>Environmental risk, measured.</h1><p>AI-assisted assessment of climate indicators, operational impact and environmental risk for data-driven decisions.</p></div><div className={"risk-ring "+riskClass(dash.risk_level)}><strong>{dash.impact_score}</strong><span>Impact score</span></div></div>
<div className="grid kpis"><K title="Environmental Risk" value={dash.risk_level} note="AI assessment" cls={riskClass(dash.risk_level)}/><K title="Estimated CO₂" value={dash.estimated_co2_kg+" kg"} note="Latest observation"/><K title="Energy" value={dash.latest.energy_kwh+" kWh"} note="Latest observation"/><K title="Air Quality" value={dash.latest.aqi} note="AQI index"/><K title="Temperature" value={dash.latest.temperature_c+" °C"} note={dash.latest.location}/></div>
<div className="grid two"><Card title="Climate & operational trend" className="trend-card"><Line data={lineData} options={lineChartOptions}/></Card><Card title="Risk distribution"><div className="donut"><Doughnut data={riskData} options={riskChartOptions} plugins={[riskLabelsPlugin]}/></div></Card></div>
<div className="grid two"><Card title="Latest environmental snapshot"><div className="snapshot">{Object.entries(dash.latest).filter(([k])=>!["id","risk_level"].includes(k)).map(([k,v])=><div><span>{k.replaceAll("_"," ")}</span><b>{typeof v==="number"?Number(v).toFixed(2):v}</b></div>)}</div></Card><Card title="Decision support"><Recommendations items={dash.recommendations}/></Card></div>
</section>}
function K({title,value,note,cls=""}){return <div className={"card kpi "+cls}><span>{title}</span><strong>{value}</strong><small>{note}</small></div>}
function Card({title,children,className=""}){return <div className={`card ${className}`}><div className="card-title">{title}</div>{children}</div>}
function DataTable({data}){return <Card title={`Environmental records (${data.length} shown)`}><div className="table-wrap"><table><thead><tr>{["date","location","temperature_c","humidity_pct","co2_ppm","aqi","energy_kwh","water_liters","renewable_pct","risk_level"].map(x=><th>{x}</th>)}</tr></thead><tbody>{data.map(r=><tr>{["date","location","temperature_c","humidity_pct","co2_ppm","aqi","energy_kwh","water_liters","renewable_pct","risk_level"].map(x=><td>{typeof r[x]==="number"?r[x].toFixed(1):r[x]}</td>)}</tr>)}</tbody></table></div></Card>}
function Prediction({onResult,result,metrics}){const [f,setF]=useState({temperature_c:30,humidity_pct:65,rainfall_mm:5,co2_ppm:450,aqi:90,water_liters:2800,renewable_pct:25,extreme_weather_index:20});
const change=(k,v)=>setF({...f,[k]:Number(v)}); async function run(e){e.preventDefault();const r=await api().post("/predict",f);onResult(r.data)}
return <div className="grid two"><Card title="AI environmental risk prediction"><form className="form-grid" onSubmit={run}>{Object.entries(f).map(([k,v])=><label>{k.replaceAll("_"," ")}<input type="number" step="any" value={v} onChange={e=>change(k,e.target.value)}/></label>)}<button className="primary">Run AI prediction</button></form></Card><Card title="Prediction result">{result?<div className="result"><span>Predicted energy consumption</span><strong>{result.predicted_energy_kwh} kWh</strong><span>Predicted environmental risk</span><b className={"badge "+result.predicted_risk.toLowerCase()}>{result.predicted_risk}</b></div>:<p className="muted">Enter scenario values and run the model. The model is trained on the included demonstration dataset.</p>}{metrics&&<div className="metrics"><b>Model evaluation</b><div>MAE <strong>{metrics.energy_model.mae}</strong></div><div>RMSE <strong>{metrics.energy_model.rmse}</strong></div><div>R² <strong>{metrics.energy_model.r2}</strong></div><div>Risk accuracy <strong>{(metrics.risk_model.accuracy*100).toFixed(1)}%</strong></div></div>}</Card></div>}
function Analytics({analytics,lineData,riskData,metrics}){return <section><div className="grid kpis"><K title="Records processed" value={analytics.total_records} note="Historical dataset"/><K title="Avg energy" value={analytics.avg_energy+" kWh"} note="Per observation"/><K title="Avg CO₂" value={analytics.avg_co2+" kg"} note="Estimated"/><K title="Model R²" value={metrics.energy_model.r2} note="Test split"/></div><div className="grid two"><Card title="Monthly energy & CO₂"><Line data={lineData} options={lineChartOptions}/></Card><Card title="Risk distribution"><div className="donut"><Doughnut data={riskData} options={riskChartOptions} plugins={[riskLabelsPlugin]}/></div></Card></div></section>}
function Alerts({alerts}){return <Card title={`Environmental alerts (${alerts.length})`}>{alerts.map(a=><div className="alert"><b>{a.risk} risk</b><span>{a.location} • {a.date}</span><p>{a.message}</p></div>)}{!alerts.length&&<p>No alerts detected.</p>}</Card>}
function Recommendations({items}){return <div>{items.map((x,i)=><div className="recommend"><span className={"dot "+x.severity.toLowerCase()}></span><div><b>{x.severity}</b><p>{x.message}</p></div></div>)}</div>}
function About(){return <div className="grid two"><Card title="Climate Change"><h3>Climate Change Impact Assessment and Environmental Risk Prediction Platform</h3><p>This academic prototype combines Big Data processing, AI/ML, cybersecurity controls and cloud-ready architecture to support climate-impact assessment and environmental decision making.</p><h4>Technology</h4><p>Python • FastAPI • React • MongoDB-ready • SQLite demo store • Pandas • Scikit-learn • Chart.js</p></Card><Card title="SDG 13 — Climate Action"><p>The platform supports climate action by turning environmental observations into impact indicators, risk predictions, anomaly alerts and decision-support recommendations.</p><h4>Data note</h4><p>The included dataset is synthetic demonstration data. It is not a substitute for official climate observations or regulatory risk assessments.</p></Card></div>}
createRoot(document.getElementById("root")).render(localStorage.getItem("token")?<App/>:<Login onLogin={()=>location.reload()}/>);
