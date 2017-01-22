@require(targets, source)
@# targets: the targets specified in the spider(s)
@# source : the news source, CNN for example
<!DOCTYPE html>
<html lang="en">
<head>
  <title>@source News Crawler</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="/assets/bootstrap.min.css">
  <link rel="stylesheet" href="/assets/custom.css">
  <script src="/assets/jquery.min.js"></script>
  <script src="/assets/bootstrap.min.js"></script>
</head>
<body>


@# this generates a tab containing lists of news
  <div class="container">
    <h2>@source News Crawler</h2>
    <ul class="nav nav-tabs">
      @for i, t in enumerate(targets.keys()):
          @if i == 0:
              <li class="active"> \
          @else:
              <li> \
          @end
          <a data-toggle="tab" href="#@t.lower()">@t</a></li>
      @end
    </ul>
    <div class="tab-content">
      @for i, t in enumerate(targets.keys()):
          @if i == 0:
              <div id="@t.lower()" class="tab-pane fade in active">
          @else:
              <div id="@t.lower()" class="tab-pane fade">
          @end

@# this generates list of news
          <ul class="nav nav-pills nav-stacked">
          @for news in targets[t]:
            <li title="<b>Story highlights</b>" data-toggle="popover" data-trigger="hover"
                data-html="true" data-content="@news.highlights">
              <button type="button" class="btn btn-info btn-lg load-preview" data-toggle="modal"
                      data-target="#newModal" fetch-source="@news.location">@news.title</button>
            </li>
          @end
          </ul>
        </div>
      @end
    </div>
  </div>

  <!-- Modal -->
  <div class="modal fade" id="myModal" role="dialog">
    <div class="modal-dialog" style="width:80%">
    
      <!-- Modal content-->
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal">&times;</button>
          <h2 class="modal-title news-header"></h2>
        </div>
        <div class="modal-body news-body">
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- enable popover -->
	<script>
	$(document).ready(function(){
			$('[data-toggle="popover"]').popover();   
	});
	</script>
</body>
</html>
