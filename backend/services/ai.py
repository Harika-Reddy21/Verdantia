def recommend_species(weather, soil):
    species=[]
    if weather.get('rainfall_mm',800)<500: species+=['Azadirachta indica (Neem)','Acacia nilotica (Babul)']
    else: species+=['Tectona grandis (Teak)','Syzygium cumini (Jamun)']
    if soil.get('texture')=='sandy': species.append('Casuarina equisetifolia (Casuarina)')
    return {'species':list(dict.fromkeys(species)),'density_per_hectare':1600,'pattern':'mixed clusters'}
def restoration_plan(soil, ndvi, climate):
    rec=['Apply 5–10 tons/ha compost'] if soil.get('organic_carbon_pct',1.0)<1.0 else []
    if ndvi<0.2: rec.append('Low NDVI – start with hardy pioneers.')
    return {'soil_improvements':rec,'pioneer_species':['Acacia catechu','Gliricidia sepium'],'secondary_species':['Shorea robusta','Tectona grandis'],'layout':'Clusters 5m dia every 20–30m'}
def compliance_eval(area_sqm, trees_planned, green_area_sqm=None):
    req=int((area_sqm/80.0)+0.999)
    cover=None if green_area_sqm is None else round((green_area_sqm/area_sqm)*100.0,2)
    compliant=trees_planned>=req or (cover is not None and cover>=10.0)
    return {'required_trees':req,'trees_planned':trees_planned,'current_cover_pct':cover,'required_cover_pct':10.0,'compliant':compliant,'delta_trees':max(0,req-trees_planned)}