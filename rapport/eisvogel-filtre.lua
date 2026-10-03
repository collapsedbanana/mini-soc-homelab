-- Filtre Pandoc pour rapport-mini-soc.md (gabarit Eisvogel)
-- Encadrés ::: {.box .key|.info|.warn} , badges [texte]{.v .ok|.mid|.ko|.fix}, saut de page avant chaque test.

local couleurs = {
  key  = {fond = "green!6",  bord = "green!45!black",  titre = "green!35!black"},
  info = {fond = "blue!5",   bord = "blue!60!black",   titre = "blue!55!black"},
  warn = {fond = "orange!8", bord = "orange!75!black", titre = "orange!65!black"},
}
local badges = {ok = "green!35!black", mid = "orange!70!black", ko = "red!65!black", fix = "blue!60!black"}

local function has(el, c) return el.classes:includes(c) end

function Span(el)
  if has(el, "v") then
    for k, col in pairs(badges) do
      if has(el, k) then
        local out = pandoc.Inlines({pandoc.RawInline("latex", "\\textcolor{" .. col .. "}{\\textsf{\\footnotesize\\bfseries[")})
        out:extend(el.content)
        out:insert(pandoc.RawInline("latex", "]}}"))
        return out
      end
    end
  end
end

local dans_resultats = false

function Div(el)
  if has(el, "box") then
    local style
    for k, v in pairs(couleurs) do if has(el, k) then style = v end end
    style = style or couleurs.info
    local titre = ""
    local blocs = {}
    for _, b in ipairs(el.content) do
      if b.t == "Div" and has(b, "ttl") then
        titre = pandoc.utils.stringify(b):gsub("&", "\\&")
      else
        table.insert(blocs, b)
      end
    end
    local debut = string.format(
      "\\begin{tcolorbox}[enhanced,breakable,colback=%s,colframe=%s,boxrule=0pt,leftrule=3pt,arc=1pt,"
      .. "left=8pt,right=8pt,top=5pt,bottom=5pt,fonttitle=\\sffamily\\bfseries\\small,coltitle=%s,"
      .. "colbacktitle=%s,title={\\MakeUppercase{%s}},attach title to upper,after title={\\par\\smallskip}]",
      style.fond, style.bord, style.titre, style.fond, titre)
    local out = {pandoc.RawBlock("latex", debut)}
    for _, b in ipairs(blocs) do table.insert(out, b) end
    table.insert(out, pandoc.RawBlock("latex", "\\end{tcolorbox}"))
    return out
  end
  if has(el, "results") then
    local out = {}
    local premier = true
    for _, b in ipairs(el.content) do
      if b.t == "Header" and b.level == 2 then
        if not premier then table.insert(out, pandoc.RawBlock("latex", "\\newpage")) end
        premier = false
      end
      table.insert(out, b)
    end
    return out
  end
end

function Header(el)
  if el.level == 1 then
    return {pandoc.RawBlock("latex", "\\newpage"), el}
  end
end
