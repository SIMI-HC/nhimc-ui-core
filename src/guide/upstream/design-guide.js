(function(){
  "use strict";
  const data=window.NHIMC_DESIGN_GALLERY;
  if(!data||!Array.isArray(data.items)||!Array.isArray(data.icons)){throw new Error("Design Guide 생성 데이터를 불러오지 못했습니다.")}

  const root=document.documentElement;
  const grid=document.getElementById("galleryGrid");
  const search=document.getElementById("gallerySearch");
  const status=document.getElementById("resultStatus");
  const empty=document.getElementById("emptyState");
  const counts=document.getElementById("galleryCounts");
  const dialog=document.getElementById("previewDialog");
  const detailFrame=document.getElementById("detailFrame");
  let activeFilter="all";
  let previewTheme="light";
  let previewThemeColor="nhimc-default";
  let lastTrigger=null;
  let openDialogCount=0;
  function lockBodyScroll(){openDialogCount+=1;document.documentElement.style.overflow="hidden";document.body.style.overflow="hidden"}
  function unlockBodyScroll(){openDialogCount=Math.max(0,openDialogCount-1);if(openDialogCount===0){document.documentElement.style.overflow="";document.body.style.overflow=""}}

  const escapeHtml=value=>String(value).replace(/[&<>"]/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[char]));
  const typeLabel={frame:"FRAME",template:"TEMPLATE",component:"COMPONENT",icon:"ICON"};
  const updateFormatter=new Intl.DateTimeFormat("ko-KR",{timeZone:"Asia/Seoul",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false});
  const formatUpdatedAt=value=>{const parts=Object.fromEntries(updateFormatter.formatToParts(new Date(value)).map(part=>[part.type,part.value]));return `${parts.year}.${parts.month}.${parts.day} ${parts.hour}:${parts.minute}`};
  const searchable=item=>[item.id,item.name,item.title,item.description,item.category,item.updatedAt||"",formatUpdatedAt(item.updatedAt),...item.tags].join(" ").toLocaleLowerCase("ko");

  if(!Array.isArray(data.themes)||!data.themes.length){throw new Error("선택 가능한 Theme 데이터를 불러오지 못했습니다.")}
  const themeById=new Map(data.themes.map(theme=>[theme.id,theme]));
  const themeOptions=document.getElementById("themeOptions");
  const themeDescription=document.getElementById("themeDescription");
  const themeRecommendation=document.getElementById("themeRecommendation");
  const themeSwatch=theme=>{
    const tokens=theme.tokens.light;
    const accents=["chip-sky","chip-pear","chip-apricot","chip-yellow","chip-purple","chip-pink"].map(name=>tokens[name]).filter(Boolean);
    if(accents.length===6)return `conic-gradient(${accents.map((color,index)=>`${color} ${index*60}deg ${(index+1)*60}deg`).join(",")})`;
    return tokens.ring&&tokens.ring!==tokens.primary?`linear-gradient(90deg, ${tokens.primary} 50%, ${tokens.ring} 50%)`:tokens.primary;
  };
  themeOptions.innerHTML=data.themes.map(theme=>`<button class="theme-option" type="button" data-theme-color-option="${escapeHtml(theme.id)}" aria-pressed="false"><span class="theme-swatch" style="--theme-swatch:${escapeHtml(themeSwatch(theme))}" aria-hidden="true"></span><span><strong>${escapeHtml(theme.label)}</strong><small>${escapeHtml(theme.summary)}</small></span></button>`).join("");

  counts.innerHTML=["frame","template","component","icon"].map(type=>`<div><dt>${typeLabel[type]}</dt><dd>${data.counts[type]}</dd></div>`).join("");

  if(!Array.isArray(data.logos)||!data.logos.length){throw new Error("일산병원 로고 데이터를 불러오지 못했습니다.")}
  document.getElementById("brandLogoOptions").innerHTML=data.logos.map(logo=>`<div class="brand-option" data-default="${logo.default}"><div class="brand-option-preview">${logo.svg}</div><strong>${escapeHtml(logo.label)}${logo.default?'<span class="default-badge">기본값</span>':""}</strong><small>${escapeHtml(logo.recommendedFor)}</small></div>`).join("");
  if(!Array.isArray(data.fonts)||!data.fonts.length){throw new Error("폰트 데이터를 불러오지 못했습니다.")}
  document.getElementById("fontOptions").innerHTML=data.fonts.map(font=>`<div class="font-option"><strong>${escapeHtml(font.family)} · ${font.weight}</strong><span style="font-weight:${font.weight}">가나다라 ABC 123 · National Health Insurance Service Ilsan Hospital</span></div>`).join("");

  const iconGrid=document.getElementById("iconGrid"),iconSearch=document.getElementById("iconSearch"),iconStatus=document.getElementById("iconStatus"),iconCategories=document.getElementById("iconCategories");
  const iconDialog=document.getElementById("iconDialog");let activeIconCategory="전체",lastIconTrigger=null;
  const iconSvg=icon=>`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icon.svg}</svg>`;
  const sortedIcons=[...data.icons].sort((a,b)=>new Date(b.updatedAt)-new Date(a.updatedAt)||a.id.localeCompare(b.id));
  const categories=["전체",...new Set(sortedIcons.map(icon=>icon.category))];
  iconCategories.innerHTML=categories.map(category=>`<button type="button" data-icon-category="${escapeHtml(category)}" aria-pressed="${category==="전체"}">${escapeHtml(category)}</button>`).join("");
  function renderIcons(){const query=iconSearch.value.trim().toLocaleLowerCase("ko"),visible=sortedIcons.filter(icon=>(activeIconCategory==="전체"||icon.category===activeIconCategory)&&(!query||`${icon.id} ${icon.label} ${icon.category}`.toLocaleLowerCase("ko").includes(query)));iconGrid.innerHTML=visible.map(icon=>`<button class="icon-card" type="button" data-icon-id="${escapeHtml(icon.id)}" data-tone="${escapeHtml(icon.tone)}" aria-label="${escapeHtml(icon.label)} 아이콘 확대 보기">${iconSvg(icon)}<strong>${escapeHtml(icon.label)}</strong><small>${escapeHtml(icon.id)}</small></button>`).join("");iconStatus.textContent=`전체 ${sortedIcons.length}종 중 ${visible.length}종 표시`}
  iconCategories.addEventListener("click",event=>{const button=event.target.closest("[data-icon-category]");if(!button)return;activeIconCategory=button.dataset.iconCategory;iconCategories.querySelectorAll("button").forEach(item=>item.setAttribute("aria-pressed",String(item===button)));renderIcons()});
  iconSearch.addEventListener("input",renderIcons);
  iconGrid.addEventListener("click",event=>{const button=event.target.closest("[data-icon-id]");if(!button)return;const icon=sortedIcons.find(item=>item.id===button.dataset.iconId);if(!icon)return;lastIconTrigger=button;document.getElementById("iconDialogTitle").textContent=icon.label;document.getElementById("iconDialogMeta").textContent=`${icon.id} · ${icon.category} · 24px round stroke`;document.getElementById("iconLarge").innerHTML=iconSvg(icon);document.getElementById("iconCode").textContent=icon.svg;iconDialog.showModal();lockBodyScroll()});
  const closeIconDialog=()=>{iconDialog.close();unlockBodyScroll();lastIconTrigger?.focus()};document.getElementById("iconDialogClose").addEventListener("click",closeIconDialog);iconDialog.addEventListener("cancel",event=>{event.preventDefault();closeIconDialog()});
  renderIcons();

  function cardTemplate(item){
    const tags=item.tags.slice(0,3).map(tag=>`<span class="tag">${escapeHtml(tag)}</span>`).join("");
    const badge=item.type==="component"?(item.layer==="atom"?"원자":"응용"):typeLabel[item.type];
    return `<article class="gallery-card" data-type="${item.type}" data-id="${escapeHtml(item.id)}">
      <button class="preview-button" type="button" aria-label="${escapeHtml(item.name)} 상세 Preview 열기">
        <span class="preview-stage"><iframe data-preview-key="${escapeHtml(item.previewSource)}" data-gallery-key="${item.type}:${escapeHtml(item.id)}" title="${escapeHtml(item.name)} UI Preview" tabindex="-1" loading="lazy"></iframe></span>
        <span class="preview-loading" aria-hidden="true"><span class="preview-loading-dot"></span></span>
        <span class="preview-zoom" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg></span>
      </button>
      <div class="card-body"><div class="card-heading"><div class="card-title-row"><h2>${escapeHtml(item.name)}</h2><span class="type-badge">${badge}</span></div><p>${escapeHtml(item.title)}</p></div><p class="description">${escapeHtml(item.description)}</p><dl class="lifecycle"><div><dt>업데이트</dt><dd><time datetime="${escapeHtml(item.updatedAt)}">${escapeHtml(formatUpdatedAt(item.updatedAt))}</time></dd></div></dl><div class="tags">${tags}</div></div>
    </article>`;
  }

  grid.innerHTML=data.items.map(cardTemplate).join("");
  const cards=[...grid.querySelectorAll(".gallery-card")];
  const itemById=new Map(data.items.map(item=>[`${item.type}:${item.id}`,item]));

  function fitPreview(card){
    const button=card.querySelector(".preview-button"),stage=card.querySelector(".preview-stage");
    if(!button||!stage)return;
    const scale=Math.min(button.clientWidth/stage.offsetWidth,button.clientHeight/stage.offsetHeight);
    stage.style.setProperty("--gallery-preview-scale",String(scale));
  }
  const fitPreviews=()=>cards.forEach(fitPreview);
  fitPreviews();
  if("ResizeObserver" in window){const resizeObserver=new ResizeObserver(entries=>entries.forEach(entry=>fitPreview(entry.target)));cards.forEach(card=>resizeObserver.observe(card))}
  else window.addEventListener("resize",fitPreviews);

  function themeDeclarations(){
    const styles=getComputedStyle(root),declarations=[];
    for(let index=0;index<styles.length;index+=1){const name=styles[index];if(name.startsWith("--color-")||name.startsWith("--radius-")||name.startsWith("--shadow-")){const value=styles.getPropertyValue(name).trim();if(value)declarations.push(`${name}:${value}!important`)}}
    return declarations.join(";");
  }
  function colorThemeRules(){
    const theme=themeById.get(previewThemeColor);
    if(!theme)return "";
    const declarations=mode=>Object.entries(theme.tokens[mode]).map(([name,value])=>`--color-${name}:${value}!important`).join(";");
    return `:root{${declarations("light")}}:root[data-theme="dark"]{${declarations("dark")}}`;
  }
  function applyPreviewTheme(frame){
    try{
      const document=frame.contentDocument;if(!document||!document.documentElement)return;
      document.documentElement.dataset.theme=previewTheme;
      document.documentElement.dataset.themeColor=previewThemeColor;
      document.documentElement.style.colorScheme=previewTheme;
      let style=document.getElementById("nhimc-gallery-theme-adapter");if(!style){style=document.createElement("style");style.id="nhimc-gallery-theme-adapter";document.head.appendChild(style)}
      const isFrame=frame.dataset.galleryKey?.startsWith("frame:");
      const surfaceAdapter=isFrame?`html,body{color-scheme:${previewTheme}!important}`:`:root{${themeDeclarations()}}html,body{color-scheme:${previewTheme}!important}body,.shell,.app{background:var(--color-canvas,var(--color-background))!important;color:var(--color-foreground)!important}aside{background-color:var(--color-sidebar-brand)!important;color:var(--color-sidebar-brand-foreground)!important}.header,header,.card,input,select,textarea,dialog{background-color:var(--color-card)!important;color:var(--color-card-foreground,var(--color-foreground))!important}th,.head,.card h2{background-color:var(--color-secondary)!important;color:var(--color-foreground)!important}tbody tr:hover td{background-color:var(--color-band-sky,var(--color-secondary))!important}`;
      const colorMixAdapter=previewThemeColor!=="color-mix"?"":`[data-nhimc-accent=sky]{--nhimc-accent-surface:var(--color-chip-sky);--nhimc-accent-foreground:var(--color-accent-sky-foreground)}[data-nhimc-accent=pear]{--nhimc-accent-surface:var(--color-chip-pear);--nhimc-accent-foreground:var(--color-accent-pear-foreground)}[data-nhimc-accent=apricot]{--nhimc-accent-surface:var(--color-chip-apricot);--nhimc-accent-foreground:var(--color-accent-apricot-foreground)}[data-nhimc-accent=yellow]{--nhimc-accent-surface:var(--color-chip-yellow);--nhimc-accent-foreground:var(--color-accent-yellow-foreground)}[data-nhimc-accent=purple]{--nhimc-accent-surface:var(--color-chip-purple);--nhimc-accent-foreground:var(--color-accent-purple-foreground)}[data-nhimc-accent=pink]{--nhimc-accent-surface:var(--color-chip-pink);--nhimc-accent-foreground:var(--color-accent-pink-foreground)}.nhimc-accent-surface{background:var(--nhimc-accent-surface)!important;color:var(--nhimc-accent-foreground)!important}.nhimc-accent-icon{color:var(--nhimc-accent-foreground)!important}.nav-link:nth-child(6n+1) .nav-chip,.nav>*:nth-child(6n+1) .chip{background:var(--color-chip-sky)!important;color:var(--color-accent-sky-foreground)!important}.nav-link:nth-child(6n+2) .nav-chip,.nav>*:nth-child(6n+2) .chip{background:var(--color-chip-pear)!important;color:var(--color-accent-pear-foreground)!important}.nav-link:nth-child(6n+3) .nav-chip,.nav>*:nth-child(6n+3) .chip{background:var(--color-chip-apricot)!important;color:var(--color-accent-apricot-foreground)!important}.nav-link:nth-child(6n+4) .nav-chip,.nav>*:nth-child(6n+4) .chip{background:var(--color-chip-yellow)!important;color:var(--color-accent-yellow-foreground)!important}.nav-link:nth-child(6n+5) .nav-chip,.nav>*:nth-child(6n+5) .chip{background:var(--color-chip-purple)!important;color:var(--color-accent-purple-foreground)!important}.nav-link:nth-child(6n) .nav-chip,.nav>*:nth-child(6n) .chip{background:var(--color-chip-pink)!important;color:var(--color-accent-pink-foreground)!important}.metrics>:nth-child(6n+1),main>.card:nth-of-type(6n+1){border-top:4px solid var(--color-chip-sky)!important}.metrics>:nth-child(6n+2),main>.card:nth-of-type(6n+2){border-top:4px solid var(--color-chip-pear)!important}.metrics>:nth-child(6n+3),main>.card:nth-of-type(6n+3){border-top:4px solid var(--color-chip-apricot)!important}.metrics>:nth-child(6n+4),main>.card:nth-of-type(6n+4){border-top:4px solid var(--color-chip-yellow)!important}.metrics>:nth-child(6n+5),main>.card:nth-of-type(6n+5){border-top:4px solid var(--color-chip-purple)!important}.metrics>:nth-child(6n),main>.card:nth-of-type(6n){border-top:4px solid var(--color-chip-pink)!important}[data-component-case=IconButton] .icon-btn,[data-component-case=InputGroup] .icon-btn{border-color:var(--color-chip-apricot)!important;background:var(--color-chip-apricot)!important;color:var(--color-accent-apricot-foreground)!important}[data-component-case=Icon] .icon-sample,[data-component-case=Tooltip] .icon-btn{color:var(--color-accent-purple-foreground)!important}[data-component-case=Avatar] .avatar:nth-child(1){background:var(--color-chip-sky)!important;color:var(--color-accent-sky-foreground)!important}[data-component-case=Avatar] .avatar:nth-child(2){background:var(--color-chip-pear)!important;color:var(--color-accent-pear-foreground)!important}[data-component-case=Avatar] .avatar:nth-child(3){background:var(--color-chip-pink)!important;color:var(--color-accent-pink-foreground)!important}`;
      style.textContent=colorThemeRules()+surfaceAdapter+colorMixAdapter;
      const componentId=frame.dataset.componentId;
      if(componentId)document.querySelectorAll("[data-component-case]").forEach(caseNode=>{caseNode.hidden=caseNode.dataset.componentCase!==componentId});
      document.querySelectorAll("iframe").forEach(child=>{const applyChild=()=>{if(!child.contentDocument)return;child.contentDocument.documentElement.dataset.theme=previewTheme;child.contentDocument.documentElement.style.colorScheme=previewTheme;let childStyle=child.contentDocument.getElementById("nhimc-gallery-theme-adapter");if(!childStyle){childStyle=child.contentDocument.createElement("style");childStyle.id="nhimc-gallery-theme-adapter";child.contentDocument.head.appendChild(childStyle)}childStyle.textContent=style.textContent};child.addEventListener("load",applyChild,{once:true});if(child.contentDocument?.readyState==="complete")applyChild()});
      frame.contentWindow.postMessage({type:"nhimc-gallery-theme",theme:previewTheme,themeColor:previewThemeColor},"*");
    }catch(error){frame.dataset.themeError="true"}
  }
  function prepareFrame(frame){if(frame.dataset.themeReady)return;frame.dataset.themeReady="true";frame.addEventListener("load",()=>applyPreviewTheme(frame))}
  function updatePreviewThemes(){document.querySelectorAll("iframe").forEach(frame=>{prepareFrame(frame);if(frame.contentDocument?.readyState==="complete")applyPreviewTheme(frame)});if(!document.getElementById("previewStructureOverlay").hidden)renderFrameOverlay()}

  function previewDocument(item){return data.documents[item.previewSource]}
  function loadFrame(frame){if(frame.dataset.loaded)return;const item=itemById.get(frame.dataset.galleryKey);if(!item)return;prepareFrame(frame);frame.dataset.loaded="true";if(item.type==="component")frame.dataset.componentId=item.id;else frame.removeAttribute("data-component-id");const card=frame.closest(".gallery-card");if(card)frame.addEventListener("load",()=>card.classList.add("is-loaded"),{once:true});frame.srcdoc=previewDocument(item)}
  const observer="IntersectionObserver" in window?new IntersectionObserver(entries=>{
    entries.forEach(entry=>{if(!entry.isIntersecting)return;const frame=entry.target.querySelector("iframe[data-preview-key]");if(frame)loadFrame(frame);observer.unobserve(entry.target)})
  },{rootMargin:"500px 0px"}):null;
  cards.forEach(card=>{if(observer)observer.observe(card);else loadFrame(card.querySelector("iframe"))});

  function applyFilters(){
    const query=search.value.trim().toLocaleLowerCase("ko");
    let visible=0;
    cards.forEach((card,index)=>{
      const item=data.items[index];
      const matchesType=activeFilter==="all"||item.type===activeFilter;
      const matchesQuery=!query||searchable(item).includes(query);
      card.hidden=!(matchesType&&matchesQuery);
      if(!card.hidden){visible+=1;fitPreview(card)}
    });
    status.textContent=`총 ${visible}개 항목 표시`;
    empty.hidden=visible!==0;
  }

  function scrollToLibraryTop(){document.getElementById("sectionLibrary").scrollIntoView({behavior:"smooth",block:"start"})}
  document.querySelectorAll(".filter").forEach(button=>button.addEventListener("click",()=>{
    activeFilter=button.dataset.filter;
    document.querySelectorAll(".filter").forEach(item=>{const active=item===button;item.classList.toggle("active",active);item.setAttribute("aria-pressed",String(active))});
    applyFilters();
    scrollToLibraryTop();
  }));
  search.addEventListener("input",()=>{applyFilters();scrollToLibraryTop()});

  const LOCK_ICON={LOCKED:"🔒",SLOT:"◇",CONFIGURABLE:"⚙"};
  function renderStructure(item){
    const rows=(item.structure||[]).map(entry=>`<li class="lock-row" data-lock="${escapeHtml(entry.lock)}"><span class="lock-icon" aria-hidden="true">${LOCK_ICON[entry.lock]||"⚙"}</span><span class="lock-role">${escapeHtml(entry.role)}</span><span class="lock-label">${escapeHtml(entry.lock)}</span></li>`).join("");
    return `<ul class="lock-map">${rows||'<li class="lock-empty">구조 정보 없음</li>'}</ul>`;
  }
  function renderContractValue(value){
    if(Array.isArray(value))return value.length?`<ul>${value.map(entry=>`<li>${renderContractValue(entry)}</li>`).join("")}</ul>`:"<p>-</p>";
    if(value&&typeof value==="object")return `<ul>${Object.entries(value).map(([key,entry])=>`<li><strong>${escapeHtml(key)}</strong>: ${renderContractValue(entry)}</li>`).join("")}</ul>`;
    return escapeHtml(String(value??"-"));
  }
  function renderContract(item){
    const entries=Object.entries(item.contract||{});
    if(!entries.length)return "<p>Contract 정보 없음</p>";
    return entries.map(([key,value])=>`<section class="contract-field"><h3>${escapeHtml(key)}</h3><div>${renderContractValue(value)}</div></section>`).join("");
  }

  const previewTabs=[...document.querySelectorAll("[data-preview-tab]")];
  const previewPanels={preview:document.getElementById("previewPanelPreview"),structure:document.getElementById("previewPanelStructure"),contract:document.getElementById("previewPanelContract")};
  const structureOverlay=document.getElementById("previewStructureOverlay");
  let currentItem=null;

  const OVERLAY_ZONES={
    LOCKED:{tone:"locked",label:"LOCKED · Shell 구조"},
    MENU:{tone:"menu",label:"MENU · Screen Manifest로 구성"},
    SLOT:{tone:"slot",label:"SLOT · Template 삽입 영역"},
  };
  let overlayThemeObserver=null;
  function clearFrameOverlay(){structureOverlay.hidden=true;structureOverlay.innerHTML="";document.getElementById("previewStructureLegend")?.remove();overlayThemeObserver?.disconnect();overlayThemeObserver=null}
  function addOverlayBox(rect,zone,label){
    const box=document.createElement("div");
    box.className="lock-overlay-box";
    box.dataset.zone=zone;
    box.style.left=`${Math.round(rect.left)}px`;box.style.top=`${Math.round(rect.top)}px`;
    box.style.width=`${Math.round(rect.width)}px`;box.style.height=`${Math.round(rect.height)}px`;
    box.innerHTML=`<span class="lock-overlay-label">${escapeHtml(label)}</span>`;
    structureOverlay.appendChild(box);
  }
  function renderFrameOverlay(){
    structureOverlay.innerHTML="";
    const doc=detailFrame.contentDocument;
    if(!doc){structureOverlay.hidden=true;return}
    previewPanels.preview.dataset.previewTheme=doc.documentElement.dataset.theme==="dark"?"dark":"light";
    const lockByRole=new Map((currentItem.structure||[]).map(entry=>[entry.role,entry.lock]));
    doc.querySelectorAll('[data-nhimc-navigation-source="manifest"][data-navigation-view="desktop"]').forEach(node=>{
      const rect=node.getBoundingClientRect();
      if(rect.width<4||rect.height<4)return;
      addOverlayBox(rect,"MENU",`⚙ ${OVERLAY_ZONES.MENU.label}`);
    });
    const lockedNodes=[...doc.querySelectorAll("[data-nhimc-role]")].filter(node=>lockByRole.get(node.dataset.nhimcRole));
    // 다른 잠금 영역을 감싸기만 하는 상위 컨테이너(app-shell, app-main 등)는
    // 안쪽 영역과 테두리가 겹쳐 보이므로 leaf 영역만 그린다.
    const leafNodes=lockedNodes.filter(node=>!lockedNodes.some(other=>other!==node&&node.contains(other)));
    leafNodes.forEach(node=>{
      const rect=node.getBoundingClientRect();
      if(rect.width<4||rect.height<4)return;
      const lock=lockByRole.get(node.dataset.nhimcRole);
      if(lock==="SLOT"){addOverlayBox(rect,"SLOT",`◇ ${OVERLAY_ZONES.SLOT.label}`);return}
      addOverlayBox(rect,"LOCKED",`🔒 ${escapeHtml(node.dataset.nhimcRole)}`);
    });
    structureOverlay.hidden=false;
    renderOverlayLegend();
    if(!overlayThemeObserver){
      overlayThemeObserver=new MutationObserver(()=>renderFrameOverlay());
      overlayThemeObserver.observe(doc.documentElement,{attributes:true,attributeFilter:["data-theme"]});
    }
  }
  function renderOverlayLegend(){
    let legend=document.getElementById("previewStructureLegend");
    if(!legend){legend=document.createElement("div");legend.id="previewStructureLegend";legend.className="lock-legend";document.getElementById("previewPanelPreview").appendChild(legend)}
    legend.innerHTML=Object.entries(OVERLAY_ZONES).map(([zone,info])=>`<span class="lock-legend-item" data-zone="${zone}"><span class="lock-legend-swatch"></span>${escapeHtml(info.label)}</span>`).join("");
  }
  function setPreviewTab(tab){
    previewTabs.forEach(button=>{const active=button.dataset.previewTab===tab;button.classList.toggle("active",active);button.setAttribute("aria-selected",String(active))});
    const isFrame=currentItem&&currentItem.type==="frame";
    const showPreview=tab==="preview"||(isFrame&&tab==="structure");
    previewPanels.preview.hidden=!showPreview;
    previewPanels.structure.hidden=isFrame?true:tab!=="structure";
    previewPanels.contract.hidden=tab!=="contract";
    if(isFrame&&tab==="structure")renderFrameOverlay();else clearFrameOverlay();
  }
  previewTabs.forEach(button=>button.addEventListener("click",()=>setPreviewTab(button.dataset.previewTab)));

  function openPreview(item,trigger){
    lastTrigger=trigger;
    currentItem=item;
    document.getElementById("previewType").textContent=typeLabel[item.type];
    document.getElementById("previewTitle").textContent=item.name;
    document.getElementById("previewDescription").textContent=item.description;
    document.getElementById("previewContext").textContent=item.previewContext;
    document.getElementById("previewLifecycle").textContent=`업데이트 ${formatUpdatedAt(item.updatedAt)}`;
    const source=document.getElementById("previewSource");source.href=item.source;source.textContent="정본 열기";
    const detailLoading=document.getElementById("detailLoading");detailLoading.hidden=false;
    detailFrame.addEventListener("load",()=>{detailLoading.hidden=true},{once:true});
    detailFrame.dataset.previewKey=item.previewSource;detailFrame.dataset.galleryKey=`${item.type}:${item.id}`;detailFrame.removeAttribute("data-loaded");loadFrame(detailFrame);
    previewPanels.structure.innerHTML=item.type==="frame"?"":renderStructure(item);
    previewPanels.contract.innerHTML=renderContract(item);
    setPreviewTab("preview");
    dialog.showModal();
    lockBodyScroll();
  }
  cards.forEach(card=>card.querySelector(".preview-button").addEventListener("click",event=>{
    const item=itemById.get(`${card.dataset.type}:${card.dataset.id}`);if(item)openPreview(item,event.currentTarget)
  }));
  function closePreview(){dialog.close();unlockBodyScroll();detailFrame.removeAttribute("srcdoc");detailFrame.removeAttribute("data-loaded");if(lastTrigger)lastTrigger.focus()}
  document.getElementById("previewClose").addEventListener("click",closePreview);
  dialog.addEventListener("cancel",event=>{event.preventDefault();closePreview()});
  dialog.addEventListener("click",event=>{const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)closePreview()});

  const themeButton=document.getElementById("themeToggle"),themeLabel=document.getElementById("themeLabel");
  const setTheme=theme=>{previewTheme=theme;root.dataset.theme=theme;const dark=theme==="dark",label=dark?"라이트 Preview로 전환":"다크 Preview로 전환";themeLabel.textContent=dark?"라이트 Preview":"다크 Preview";themeButton.setAttribute("aria-label",label);themeButton.title=label;updatePreviewThemes()};
  const setThemeColor=themeId=>{
    const theme=themeById.get(themeId);if(!theme)return;
    previewThemeColor=themeId;root.dataset.themeColor=themeId;
    themeDescription.textContent=theme.summary;
    themeRecommendation.textContent=theme.recommendedFor;
    themeOptions.querySelectorAll("[data-theme-color-option]").forEach(button=>{const active=button.dataset.themeColorOption===themeId;button.classList.toggle("active",active);button.setAttribute("aria-pressed",String(active))});
    updatePreviewThemes();
  };
  themeOptions.addEventListener("click",event=>{const button=event.target.closest("[data-theme-color-option]");if(button)setThemeColor(button.dataset.themeColorOption)});
  themeButton.addEventListener("click",()=>setTheme(previewTheme==="dark"?"light":"dark"));
  setThemeColor(themeById.has(previewThemeColor)?previewThemeColor:data.themes[0].id);
  setTheme("light");

  // Prompt Builder: Layout/Template/Theme를 골라 다른 대화에 그대로 붙여넣을 프롬프트를 만든다.
  const builderDialog=document.getElementById("promptBuilderDialog");
  const builderOpen=document.getElementById("builderOpen");
  const builderClose=document.getElementById("builderClose");
  const builderLayoutOptions=document.getElementById("builderLayoutOptions");
  const builderThemeOptions=document.getElementById("builderThemeOptions");
  const builderRequirements=document.getElementById("builderRequirements");
  const builderPrompt=document.getElementById("builderPrompt");
  const builderCopy=document.getElementById("builderCopy");
  const builderCopyStatus=document.getElementById("builderCopyStatus");
  const FRAME_DISPLAY_ORDER={"top-left":0,top:1,left:2};
  const frameItems=data.items.filter(item=>item.type==="frame").slice().sort((a,b)=>{
    const ra=FRAME_DISPLAY_ORDER[a.id],rb=FRAME_DISPLAY_ORDER[b.id];
    if(ra!==undefined&&rb!==undefined)return ra-rb;
    if(ra!==undefined)return -1;
    if(rb!==undefined)return 1;
    return 0;
  });
  const builderState={frame:null,theme:null};

  function previewStageMarkup(item){
    return `<span class="preview-button" tabindex="-1"><span class="preview-stage"><iframe data-preview-key="${escapeHtml(item.previewSource)}" data-gallery-key="${item.type}:${escapeHtml(item.id)}" tabindex="-1" loading="lazy"></iframe></span><span class="preview-zoom" data-zoom-key="${item.type}:${escapeHtml(item.id)}" tabindex="-1" title="크게 보기"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg></span></span>`;
  }
  function mountBuilderPreviews(container){
    container.querySelectorAll(".builder-option-preview").forEach(card=>{
      const frame=card.querySelector("iframe");
      if(frame)loadFrame(frame);
    });
  }
  function fitAllBuilderPreviews(){
    builderDialog.querySelectorAll(".builder-option-preview").forEach(card=>{card.classList.add("is-loaded");fitPreview(card)});
  }
  let builderLayoutRendered=false,builderThemeRendered=false;
  const aiRecommendOption=(hint)=>`<button type="button" class="builder-option builder-option-ai" data-ai-recommend="true"><span class="builder-ai-badge" aria-hidden="true">AI</span><strong>AI 추천</strong><small>${escapeHtml(hint)}</small></button>`;
  function renderBuilderLayoutOptions(){
    if(builderLayoutRendered)return;
    builderLayoutRendered=true;
    builderLayoutOptions.innerHTML=aiRecommendOption("업무 요구사항에 맞춰 AI가 Layout을 선택합니다")+frameItems.map(item=>`<button type="button" class="builder-option builder-option-preview" data-builder-frame="${escapeHtml(item.id)}" aria-pressed="${builderState.frame===item.id}">${previewStageMarkup(item)}<strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.description)}</small></button>`).join("");
    mountBuilderPreviews(builderLayoutOptions);
    updateBuilderLayoutSelection();
  }
  function updateBuilderLayoutSelection(){
    builderLayoutOptions.querySelectorAll("[data-builder-frame]").forEach(button=>{
      button.setAttribute("aria-pressed",String(builderState.frame===button.dataset.builderFrame));
    });
    const aiButton=builderLayoutOptions.querySelector("[data-ai-recommend]");
    if(aiButton)aiButton.setAttribute("aria-pressed",String(!builderState.frame));
  }
  function renderBuilderThemeOptions(){
    if(builderThemeRendered)return;
    builderThemeRendered=true;
    builderThemeOptions.innerHTML=data.themes.map(theme=>`<button type="button" class="builder-option" data-builder-theme="${escapeHtml(theme.id)}" aria-pressed="${builderState.theme===theme.id}"><span class="theme-swatch" style="--theme-swatch:${escapeHtml(themeSwatch(theme))}" aria-hidden="true"></span><strong>${escapeHtml(theme.label)}</strong><small>${escapeHtml(theme.summary)}</small></button>`).join("");
  }
  function updateBuilderThemeSelection(){
    builderThemeOptions.querySelectorAll("[data-builder-theme]").forEach(button=>{
      button.setAttribute("aria-pressed",String(builderState.theme===button.dataset.builderTheme));
    });
  }
  function updateBuilderPrompt(){
    const frame=frameItems.find(item=>item.id===builderState.frame);
    const theme=builderState.theme?themeById.get(builderState.theme):null;
    const lines=["NHIMC Worktool 스킬로 화면을 만들어줘."];
    lines.push(`frame: ${builderState.frame||"(미선택 - AI 추천)"}${frame?` — ${frame.name}`:""}`);
    lines.push("template: AI 추천");
    lines.push(`theme: ${builderState.theme||"(미선택 - AI 추천)"}${theme?` — ${theme.label}`:""}`);
    const requirement=builderRequirements.value.trim();
    lines.push(`requirements: ${requirement||"[여기에 원하는 화면 내용을 적어주세요]"}`);
    builderPrompt.textContent=lines.join("\n");
    builderCopy.disabled=!(builderState.frame||builderState.theme||requirement);
  }
  function openBuilderZoom(event){
    const zoom=event.target.closest("[data-zoom-key]");if(!zoom)return false;
    event.preventDefault();event.stopPropagation();
    const item=itemById.get(zoom.dataset.zoomKey);if(item)openPreview(item,zoom);
    return true;
  }
  builderLayoutOptions.addEventListener("click",event=>{
    if(openBuilderZoom(event))return;
    const aiButton=event.target.closest("[data-ai-recommend]");
    if(aiButton){builderState.frame=null;updateBuilderLayoutSelection();updateBuilderPrompt();return}
    const button=event.target.closest("[data-builder-frame]");if(!button)return;
    builderState.frame=builderState.frame===button.dataset.builderFrame?null:button.dataset.builderFrame;
    updateBuilderLayoutSelection();updateBuilderPrompt();
  });
  builderThemeOptions.addEventListener("click",event=>{
    const button=event.target.closest("[data-builder-theme]");if(!button)return;
    builderState.theme=builderState.theme===button.dataset.builderTheme?null:button.dataset.builderTheme;
    updateBuilderThemeSelection();updateBuilderPrompt();
    if(builderState.theme)setThemeColor(builderState.theme);
  });
  builderRequirements.addEventListener("input",updateBuilderPrompt);
  function openBuilder(){
    if(!builderState.theme&&themeById.has(previewThemeColor))builderState.theme=previewThemeColor;
    renderBuilderLayoutOptions();renderBuilderThemeOptions();updateBuilderPrompt();
    lastTrigger=builderOpen;
    builderDialog.showModal();
    lockBodyScroll();
    requestAnimationFrame(fitAllBuilderPreviews);
  }
  builderOpen.addEventListener("click",openBuilder);
  const closeBuilder=()=>{builderDialog.close();unlockBodyScroll();if(lastTrigger)lastTrigger.focus()};
  builderClose.addEventListener("click",closeBuilder);
  builderDialog.addEventListener("cancel",event=>{event.preventDefault();closeBuilder()});
  builderDialog.addEventListener("click",event=>{const rect=builderDialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)closeBuilder()});
  builderCopy.addEventListener("click",async()=>{
    const text=builderPrompt.textContent;
    let copied=false;
    try{await navigator.clipboard.writeText(text);copied=true}
    catch(error){
      try{
        const helper=document.createElement("textarea");
        helper.value=text;helper.style.position="fixed";helper.style.opacity="0";
        document.body.appendChild(helper);helper.focus();helper.select();
        copied=document.execCommand("copy");
        document.body.removeChild(helper);
      }catch(fallbackError){copied=false}
    }
    builderCopyStatus.textContent=copied?"복사됐습니다.":"복사에 실패했습니다. 프롬프트를 직접 선택해 복사해주세요.";
    if(copied)setTimeout(()=>{builderCopyStatus.textContent=""},2500);
  });

  // Section nav: 우측 고정 이동 + scroll-spy 강조
  const sectionNavLinks=[...document.querySelectorAll("#sectionNav [data-nav-target]")];
  const sectionTargets=sectionNavLinks.map(link=>document.getElementById(link.dataset.navTarget)).filter(Boolean);
  let activeSectionId=null;
  let flashedLink=null;
  let flashTimer=null;
  function setActiveSection(id){
    const changed=id!==activeSectionId;
    activeSectionId=id;
    sectionNavLinks.forEach(link=>{
      const active=link.dataset.navTarget===id;
      if(active)link.setAttribute("aria-current","true");else link.removeAttribute("aria-current");
    });
    if(!changed)return;
    if(flashTimer)clearTimeout(flashTimer);
    if(flashedLink)flashedLink.classList.remove("section-nav-flash");
    const newLink=sectionNavLinks.find(link=>link.dataset.navTarget===id);
    if(!newLink){flashedLink=null;return}
    newLink.classList.add("section-nav-flash");
    flashedLink=newLink;
    flashTimer=setTimeout(()=>{newLink.classList.remove("section-nav-flash");flashedLink=null},1400);
  }
  sectionNavLinks.forEach(link=>link.addEventListener("click",event=>{
    event.preventDefault();
    const target=document.getElementById(link.dataset.navTarget);
    if(target){target.scrollIntoView({behavior:"smooth",block:"start"});setActiveSection(link.dataset.navTarget)}
  }));
  if(sectionTargets.length){
    const scrollLine=()=>parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--gallery-header"))+40;
    let spyTicking=false;
    function updateScrollSpy(){
      spyTicking=false;
      const line=scrollLine();
      let current=sectionTargets[0];
      sectionTargets.forEach(target=>{if(target.getBoundingClientRect().top<=line)current=target});
      setActiveSection(current.id);
    }
    window.addEventListener("scroll",()=>{if(spyTicking)return;spyTicking=true;requestAnimationFrame(updateScrollSpy)},{passive:true});
    window.addEventListener("resize",()=>{if(spyTicking)return;spyTicking=true;requestAnimationFrame(updateScrollSpy)});
    updateScrollSpy();
  }

  applyFilters();
})();
