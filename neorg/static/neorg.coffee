#### Open neighboring image
#
# The first argument `arrow` must be a string in `arrowKeyArray`.
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


#### Helper function for `bindKeydownToNeorgCBOpen`
bindKeydown = (key, func) ->
  $(document).bind "keydown.neorg." + key, key, func


#### Bind arrow keys using [jquery.hotkeys]
#
# [jquery.hotkeys]: https://github.com/tzuryby/jquery.hotkeys/
bindKeydownToNeorgCBOpen = (key) ->
  bindKeydown key, (e) ->
    e.preventDefault()
    neorgCBOpen key


#### Unbind arrow keys; called via colorbox's `onClosed`
unBindKeydown = (key) ->
  $(document).unbind "keydown.neorg." + key

arrowKeyArray = [ "left", "right", "up", "down" ]


#### Setting for [colorbox] plugin
#
# [colorbox]: http://jacklmoore.com/colorbox/
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


#### Colorize dictdiff table using [jquery.heatcolor] plugin
#
# [jquery.heatcolor]: http://www.jnathanson.com/blog/client/jquery/heatcolor/
neorgDictDiffInit = ->
  $("table.neorg-dictdiff").each ->
    ncolsList = ($(e).find("td").length for e in $(this).find("tr"))
    ncols = Math.max ncolsList...

    for column in [1..ncols]
      console.log column
      console.log $(this).find("tr > td:nth-child(" + column + ")")[1..]
        .heatcolor -> $(this).text()


#### Dynamically load text area to edit current page
#
# This function will be invoked by clicking `a.page-action-edit`
neorgEdit = (e) ->
  e.preventDefault()
  $("#edit-form-wrapper").html "<p>Loading...</p>"
  $.ajax
    url: "_edit_form"
    success: (data) ->
      $("#edit-form-wrapper").html data
      $("#edit-form-textarea").focus()
      return


#### Initialize everything for a neorg page
#
neorgInit = ->
  $(".neorg-gene-image-link").colorbox neorgCBSetting

  neorgDictDiffInit()

  $("a.page-action-edit").click neorgEdit
  $("#edit-form-textarea").focus()


#### Export `neorgInit` as a global function
# see: <http://stackoverflow.com/questions/4214731/>
root = exports ? this
root.neorgInit = neorgInit
