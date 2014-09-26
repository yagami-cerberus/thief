$(function() {
    $("#add-product-btn").bind("click", function() {
        $("#add-product-modal").modal({
            "keyboard": true
        });
    });
    
    var $st = $("[data-new-product=status]", $("#add-product-modal"));
    $("[data-new-product=create-btn]").bind("click", function() {
        $f = $("form", $("#add-product-modal"));
        if(!$("[name=model_id]", $f).val()) {
            alert("請輸入型號");
            return;
        }
        data = $f.serialize()
        
        $("a,button,input", $("#add-product-modal")).prop("disabled", true);
        $st.show().text("處理中...");
        $.ajax({
            url: $f.attr("action"),
            data: data,
            dataType: "json",
            type: $f.attr("method"),
            success: function(result) {
                $("a,button,input", $("#add-product-modal")).prop("disabled", false);
                if(result.st) {
                    window.location = result.url;
                } else 
                {
                    $st.text(result.error);
                }
            },
            error: function(xhr) {
                $("a,button,input", $("#add-product-modal")).prop("disabled", false);
                $st.text("系統錯誤");
            }
        });
    });
    // $("[data-role=st]", $element).text("處理中...");
    // $.ajax("{% url 'vendor_import_item' 'json' %}", {type: "post", dataType:"json",
    //   data: $f.serialize(), success: function(result) {
    //     if(result.st)
    //       $("[data-role=st]", $element)
    //         .text("")
    //         .append($("<span>OK</span>"))
    //         .append($("<a>檢視</a>").attr('href', result.url));
    //   }, error: function() {
    //     $("[data-role=st]", $element).text("系統錯誤")
    //   }
    // });
    
});