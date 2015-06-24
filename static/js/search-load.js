var cats = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        // `states` is an array of state names defined in "The Basics"
        local: availableTags
        
      });
      function categoryDefaults(q, sync) {
        if (q === '') {
         sync(cats.get('bridge', 'castle','forest_path', 'sea_cliff'));
        }
 
        else {
         cats.search(q, sync);
        }
      };
      $('#srch-term').typeahead({
        hint: true,
        highlight: true,
        minLength: 0


      },
      {

        limit: 200,
        name: 'Scenes',
        source: categoryDefaults
      });


      $body = $("body");

      $(document).on({
        ajaxStart: function() { $body.addClass("loading");    },
        ajaxStop: function() { $body.removeClass("loading"); }    
      });