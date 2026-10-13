import os, math, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from datetime import date, timedelta
from rpn import Calc, hr
os.makedirs("assets", exist_ok=True)
INK="#1f2933"; GRID="#d9dee3"; BLUE="#2563eb"; ORANGE="#e8702a"; GREEN="#2f9e44"; GREY="#8a949e"; PURPLE="#7048e8"; GOLD="#f2a900"; RED="#c92a2a"
plt.rcParams.update({"font.size":11,"axes.edgecolor":INK,"axes.labelcolor":INK,"xtick.color":INK,"ytick.color":INK,
 "text.color":INK,"axes.spines.top":False,"axes.spines.right":False,"axes.grid":True,"grid.color":GRID,"grid.linewidth":0.8,
 "figure.facecolor":"white","axes.facecolor":"white","svg.fonttype":"path","axes.titleweight":"bold","axes.titlesize":13})
PREVIEW=os.environ.get("PREVIEW")
def save(fig,name):
    fig.savefig(f"assets/{name}.svg",bbox_inches="tight",facecolor="white")
    if PREVIEW: fig.savefig(f"/tmp/nv_{name}.png",bbox_inches="tight",facecolor="white",dpi=70)
    plt.close(fig)
def box(ax,x,y,w,h,c,lw=1.8,fc="white"): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0,rounding_size=.08",fc=fc,ec=c,lw=lw))
def mdy(d): return float(f"{d.month}.{d.day:02d}{d.year}")
F=Calc('NAVIGATION.d32')
def sun_at(d,t_hours,lat=48.4284,lon=-123.3656):   # runs LBL W
    F.v.update(N=lat,E=lon,T=t_hours); F.v['C']=float(__import__('emu').J(f"{mdy(d):.6f}")-__import__('emu').J("12.311991"))
    F.st=[0.0]*4; F.lift=True; F.run('W'); return F.st[0],F.st[1]   # altitude, azimuth

# 1 Program map
fig,ax=plt.subplots(figsize=(10,3.6)); ax.axis("off"); ax.set_xlim(0,10.2); ax.set_ylim(0,3.45)
ax.text(.1,3.3,"Program Map",fontsize=13,fontweight="bold",va="center")
groups=[("Sun",GOLD,[("R","Sunrise"),("S","Sunset"),("D","Full day"),("P","Sun position")],.1),("Navigation",BLUE,[("C","CPA"),("G","Great circle")],6.3)]
for name,c,items,x0 in groups:
    ax.text(x0,2.75,name,fontsize=11.5,fontweight="bold",color=c)
    for i,(k,t) in enumerate(items):
        box(ax,x0+i*1.5,1.35,1.35,1.15,c)
        ax.text(x0+i*1.5+.675,2.08,f"LBL {k}",ha="center",fontsize=12,fontweight="bold",color=c)
        ax.text(x0+i*1.5+.675,1.68,t,ha="center",fontsize=10)
ax.text(.1,.75,"Internal: Q (location and date), W (sun position), V (SOLVE function), A and B (rise and set solvers), X, Y, Z (CPA helpers)",fontsize=9.5,color=GREY)
ax.text(.1,.3,"Flag 0: clear = use the stored default location; set = prompt for latitude and longitude",fontsize=9.5,color=GREY)
save(fig,"program_map")

# 2 Dependencies
fig,ax=plt.subplots(figsize=(10,3.4)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,3.4)
box(ax,3.6,1.1,2.8,1.1,ORANGE,lw=2.4); ax.text(5,1.77,"NAVIGATION",ha="center",fontsize=13,fontweight="bold",color=ORANGE); ax.text(5,1.4,"active State",ha="center",fontsize=9.5,color=GREY)
box(ax,.2,1.1,2.6,1.1,BLUE); ax.text(1.5,1.77,"DATETIME",ha="center",fontsize=12,fontweight="bold",color=BLUE); ax.text(1.5,1.4,"datetime32",ha="center",fontsize=9.5,color=GREY)
box(ax,7.2,1.1,2.6,1.1,GREEN); ax.text(8.5,1.77,"CONVERSION",ha="center",fontsize=12,fontweight="bold",color=GREEN); ax.text(8.5,1.4,"conversion32",ha="center",fontsize=9.5,color=GREY)
ax.add_patch(FancyArrowPatch((3.55,1.95),(2.85,1.95),arrowstyle="-|>",mutation_scale=16,color=BLUE,lw=1.8,connectionstyle="arc3,rad=-0.5"))
ax.add_patch(FancyArrowPatch((3.55,1.35),(2.85,1.35),arrowstyle="-|>",mutation_scale=16,color=BLUE,lw=1.8,connectionstyle="arc3,rad=0.5"))
ax.add_patch(FancyArrowPatch((6.45,1.65),(7.15,1.65),arrowstyle="-|>",mutation_scale=16,color=GREEN,lw=1.8))
ax.text(.2,2.75,"Q13  XEQ N:DATETIME   days since 12.31.1991",fontsize=9.5,color=BLUE,family="DejaVu Sans Mono")
ax.text(.2,.45,"D09  XEQ T:DATETIME   day length",fontsize=9.5,color=BLUE,family="DejaVu Sans Mono")
ax.text(9.8,2.75,"G38  XEQ C:CONVERSION   nm to km",fontsize=9.5,color=GREEN,family="DejaVu Sans Mono",ha="right")
ax.text(0,3.3,"Remote XEQ Dependencies",fontsize=13,fontweight="bold",va="center")
save(fig,"dependencies")

# 3 Daylight over the year
days=[date(2024,1,1)+timedelta(i) for i in range(0,366)]
rise=[];sett=[]
for d in days:
    c=Calc('NAVIGATION.d32',inputs={'D':mdy(d)}); c.run('D'); sett.append(hr(c.st[0])); rise.append(hr(c.st[1]))
x=np.array([(d-date(2024,1,1)).days for d in days])
fig,ax=plt.subplots(figsize=(10,4.4))
ax.fill_between(x,rise,sett,color=GOLD,alpha=.25,lw=0,label="Daylight")
ax.plot(x,rise,color=ORANGE,lw=2.2,label="Sunrise (LBL R)"); ax.plot(x,sett,color=PURPLE,lw=2.2,label="Sunset (LBL S)")
L=np.array(sett)-np.array(rise); i1,i2=int(np.argmax(L)),int(np.argmin(L))
for i,c in ((i1,GREEN),(i2,BLUE)):
    ax.annotate(f"{days[i]:%b %d}: {int(L[i])} h {int(round((L[i]%1)*60))} min",xy=(x[i],(rise[i]+sett[i])/2),ha="right" if x[i]>300 else "center",fontsize=10,color=c,fontweight="bold")
ax.set_xticks([(date(2024,m,1)-date(2024,1,1)).days for m in range(1,13)]); ax.set_xticklabels([date(2024,m,1).strftime("%b") for m in range(1,13)])
ax.set_yticks(range(4,24,2)); ax.set_yticklabels([f"{h:02d}:00" for h in range(4,24,2)]); ax.set_ylim(4,23); ax.set_xlim(0,365)
ax.set_ylabel("Time (UTC−7)"); ax.legend(frameon=False,loc="upper right",ncol=3,fontsize=9.5,bbox_to_anchor=(1,1.02))
ax.set_title("Sunrise, Sunset and Daylight in Victoria, BC, 2024",loc="left",pad=18); save(fig,"daylight_year")

# 4 SOLVE illustration
d=date(2024,6,20); ts=np.linspace(0,24,300); alt=np.array([sun_at(d,t)[0]+0.8333 for t in ts])
c=Calc('NAVIGATION.d32',inputs={'D':mdy(d)}); c.run('D'); sr,ss=hr(c.st[1]),hr(c.st[0])
fig,ax=plt.subplots(figsize=(10,4.3))
ax.plot(ts,alt,color=INK,lw=2.2,label="LBL V: altitude + 0.8333°")
ax.axhline(0,color=GREY,lw=1)
ax.fill_between(ts,alt,0,where=alt>0,color=GOLD,alpha=.2,lw=0)
for g,r,lab,c in ((4,sr,"LBL A",ORANGE),(16,ss,"LBL B",PURPLE)):
    ax.plot(g,sun_at(d,g)[0]+.8333,"s",color=c,ms=9,zorder=5,mfc="white",mew=2)
    ax.annotate("",xy=(r,0),xytext=(g,sun_at(d,g)[0]+.8333),arrowprops=dict(arrowstyle="-|>",color=c,lw=1.6,connectionstyle="arc3,rad=.25"))
    ax.plot(r,0,"o",color=c,ms=10,zorder=6)
    h=int(r); m=int((r-h)*60); s=round(((r-h)*60-m)*60)
    ax.text(1.0 if lab=="LBL A" else 23.6,24,f"{lab}: guess {g:02d}:00 →\nroot {h:02d}:{m:02d}:{s:02d}",ha="left" if lab=="LBL A" else "right",fontsize=10,color=c,fontweight="bold")
ax.set_xticks(range(0,25,3)); ax.set_xticklabels([f"{h:02d}:00" for h in range(0,25,3)]); ax.set_xlim(0,24); ax.set_ylim(-25,70)
ax.set_xlabel("Local time T (UTC−7)"); ax.set_ylabel("Degrees"); ax.legend(frameon=False,loc="upper left",fontsize=9.5)
ax.set_title("SOLVE Finds Sunrise and Sunset: June 20, 2024, Victoria",loc="left"); save(fig,"rise_set_solve")

# 5 Sun path
fig,ax=plt.subplots(figsize=(10,4.4))
for d,lab,c in ((date(2024,6,20),"June 20",ORANGE),(date(2024,3,20),"March 20",GREEN),(date(2024,12,21),"December 21",BLUE)):
    pts=[sun_at(d,t) for t in np.linspace(3,23,400)]; a=np.array([p[0] for p in pts]); z=np.array([p[1] for p in pts])%360
    m=a>-1; ax.plot(z[m],a[m],color=c,lw=2.4,label=lab)
alt,az=sun_at(date(2024,6,20),hr(13.15)); ax.plot(az,alt,"o",color=RED,ms=10,zorder=5)
ax.annotate(f"LBL P, 13:15 June 20:\nazimuth {az:.2f}°, altitude {alt:.2f}°",xy=(az,alt),xytext=(232,66),fontsize=10,color=RED,arrowprops=dict(arrowstyle="->",color=RED))
ax.axhline(0,color=INK,lw=1); ax.set_xlim(30,330); ax.set_ylim(-3,78)
ax.set_xticks([45,90,135,180,225,270,315]); ax.set_xticklabels(["NE 45°","E 90°","SE 135°","S 180°","SW 225°","W 270°","NW 315°"])
ax.set_xlabel("Azimuth"); ax.set_ylabel("Altitude (°)"); ax.legend(frameon=False,loc="upper left",fontsize=9.5)
ax.set_title("The Sun's Path Across the Sky, Victoria, BC",loc="left"); save(fig,"sun_path")

# 6 CPA plot
S,B,R,Cc,V=12,45,10,270,15
px,py=R*math.sin(math.radians(B)),R*math.cos(math.radians(B)); vx,vy=V*math.sin(math.radians(Cc)),V*math.cos(math.radians(Cc))-S
t=-(px*vx+py*vy)/(vx*vx+vy*vy); ix,iy=px+vx*t,py+vy*t
fig,ax=plt.subplots(figsize=(7.5,6.6)); ax.set_aspect("equal")
for r in (2,4,6,8,10): ax.add_patch(Circle((0,0),r,fill=False,ec=GRID,lw=1))
ax.annotate("",xy=(0,3),xytext=(0,0),arrowprops=dict(arrowstyle="-|>",color=BLUE,lw=2.4)); ax.plot(0,0,"o",color=BLUE,ms=10,zorder=5)
ax.text(.3,-.7,"Own ship\n12 kn, heading up",fontsize=10,color=BLUE)
ax.plot(px,py,"o",color=ORANGE,ms=10,zorder=5); ax.text(px+.3,py+.3,"Target\nbearing 045°, 10 nm",fontsize=10,color=ORANGE)
ax.annotate("",xy=(px+vx*t*1.25,py+vy*t*1.25),xytext=(px,py),arrowprops=dict(arrowstyle="-|>",color=ORANGE,lw=2,linestyle="--"))
ax.plot([0,ix],[0,iy],color=RED,lw=2); ax.plot(ix,iy,"o",color=RED,ms=9,zorder=5)
ax.text(-3.2,3.2,f"CPA {math.hypot(ix,iy):.2f} nm\nin {t*60:.1f} min\nat {math.degrees(math.atan2(ix,iy)):.1f}°",fontsize=10,color=RED,ha="right",fontweight="bold")
ax.text(-10.5,10.6,"Target: course 270° relative, 15 kn",fontsize=10,color=ORANGE)
ax.set_xlim(-11,11); ax.set_ylim(-4,11.5); ax.set_xlabel("nm across (starboard +)"); ax.set_ylabel("nm ahead")
ax.set_title("Relative Motion and CPA (Example 6.6)",loc="left"); save(fig,"cpa_plot")

# 7 Great circle
def gc_points(l1,o1,l2,o2,n=100):
    p1,q1,p2,q2=map(math.radians,(l1,o1,l2,o2))
    A=np.array([math.cos(p1)*math.cos(q1),math.cos(p1)*math.sin(q1),math.sin(p1)]); Bv=np.array([math.cos(p2)*math.cos(q2),math.cos(p2)*math.sin(q2),math.sin(p2)])
    om=math.acos(A@Bv); out=[]
    for f in np.linspace(0,1,n):
        v=(math.sin((1-f)*om)*A+math.sin(f*om)*Bv)/math.sin(om); out.append((math.degrees(math.atan2(v[1],v[0])),math.degrees(math.asin(v[2]))))
    return np.array(out)
g=gc_points(48.4284,-123.3656,21.3069,-157.8583)
fig,ax=plt.subplots(figsize=(9,5.2))
ax.plot([-123.3656,-157.8583],[48.4284,21.3069],color=GREY,ls="--",lw=1.5,label="Straight line on this chart")
ax.plot(g[:,0],g[:,1],color=BLUE,lw=2.6,label="Great circle (LBL G)")
ax.plot(-123.3656,48.4284,"o",color=ORANGE,ms=10); ax.text(-123.0,49.5,"Victoria",fontsize=11,color=ORANGE,fontweight="bold")
ax.plot(-157.8583,21.3069,"o",color=GREEN,ms=10); ax.text(-158.5,19.0,"Honolulu",fontsize=11,color=GREEN,fontweight="bold")
ax.annotate("Initial course 237.71°",xy=(-124.5,47.6),xytext=(-136,51.5),fontsize=10,color=BLUE,arrowprops=dict(arrowstyle="->",color=BLUE))
ax.text(-141,24.5,"2,316.88 nm\n4,290.86 km",fontsize=11,color=BLUE,fontweight="bold")
ax.set_xlabel("Longitude (°)"); ax.set_ylabel("Latitude (°)"); ax.set_xlim(-162,-118); ax.set_ylim(17,54); ax.set_aspect(1/math.cos(math.radians(35)))
ax.legend(frameon=False,loc="lower right",fontsize=9.5)
ax.set_title("Great-Circle Route: Victoria to Honolulu (Example 6.7)",loc="left"); save(fig,"great_circle")
