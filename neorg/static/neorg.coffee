neorgCBOpen = (arrow) ->
  ctd = $.colorbox.element().parent()
  if arrow == "left"
    otd = ctd.prev()
  else if arrow == "right"
    otd = ctd.next()
  else
    ctr = ctd.parent()
    idx = ctr.children().index(ctd[0])

    return if idx == undefined
    if arrow == "up"
      otr = ctr.prev()
    else if arrow == "down"
        otr = ctr.next()
    otd = otr.children().eq(idx)

  oa = otd.children("a.neorg-gene-image-link").first()
  oa.click() if oa.length

bindKeydown = (key, func) ->
  $(document).bind "keydown.neorg." + key, key, func

bindKeydownToNeorgCBOpen = (key) ->
  bindKeydown key, (e) ->
    e.preventDefault()
    neorgCBOpen key

unBindKeydown = (key) ->
  $(document).unbind "keydown.neorg." + key

arrowKeyArray = [ "left", "right", "up", "down" ]

neorgCBSetting =
  title: ->
    $(this).attr "title", $(this).prev("p").text()
    return  # return nothing

  transition: "none"
  speed: 0
  maxWidth: "100%"
  maxHeight: "100%"
  fixed: true
  onOpen: ->
    for i of arrowKeyArray
      bindKeydownToNeorgCBOpen arrowKeyArray[i]

  onClosed: ->
    for i of arrowKeyArray
      unBindKeydown arrowKeyArray[i]


neorgDictDiffInit = ->
  $("table.neorg-dictdiff").each ->
    ncolsList = ($(e).find("td").length for e in $(this).find("tr"))
    ncols = Math.max ncolsList...

    for column in [1..ncols]
      console.log column
      console.log $(this).find("tr > td:nth-child(" + column + ")")[1..]
        .heatcolor -> $(this).text()


neorgEdit = ->
  $("#edit-form-wrapper").html "<p>Loading...</p>"
  $.ajax
    url: "_edit_form"
    success: (data) ->
      $("#edit-form-wrapper").html data
      $("#edit-form-textarea").focus()
      return
  return false


neorgInit = ->
  $(".neorg-gene-image-link").colorbox neorgCBSetting

  neorgDictDiffInit()

  $("a.page-action-edit").click neorgEdit
  $("#edit-form-textarea").focus()


# export functions as global function
# see: http://stackoverflow.com/questions/4214731/
root = exports ? this
root.neorgInit = neorgInit
