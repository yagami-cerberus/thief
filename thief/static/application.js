MESSAGE = {
    AMAZON_FLOW_CONTROL: "AMAZON 流量管制",
    BAD_CATALOG: "品項錯誤",
    BAD_MODEL_ID: "型號錯誤",
    ITEM_ALREADY_EXIST: "產品已經存在！"
};

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
                } else if(!result.st && result.url && result.message) {
                    alert(MESSAGE[result.message]);
                    window.location = result.url;
                } else {
                    $st.text(result.error);
                }
            },
            error: function(xhr) {
                $("a,button,input", $("#add-product-modal")).prop("disabled", false);
                $st.text("系統錯誤");
            }
        });
    });
});