function delete_goal(goal_card_button) {
    document.getElementById("delete_goal_id").value=goal_card_button.parentNode.id;
    document.getElementById("confirm_delete").style.visibility='visible';
}

function update_goal(goal_card_button) {
    document.getElementById("update_goal_id").value=goal_card_button.parentNode.id;
    document.getElementById("update_goal_form").style.visibility='visible';
    var dates = goal_card_button.parentNode.querySelector("[name='dates']").attributes.value.value.split(",");
    var start_date = new Date(dates[0]);
    var end_date = new Date(dates[1]);
    start_date.setHours(start_date.getHours()+1);
    end_date.setHours(end_date.getHours()+1);
    var goal_value = goal_card_button.parentNode.querySelector("[name='goal_value']").attributes.value.value.split(",");
    
    document.getElementById("update_goal_value").value = goal_value[0];
    document.getElementById("update_start_date").valueAsDate = start_date
    document.getElementById("update_end_date").valueAsDate = end_date
    console.log(type);
    if (type=="music") {
        document.getElementById("update_goal_value").value += "%";
        document.getElementById("goal_value_type").innerText = goal_value[1];
    }
}

function add_goal() {
    document.getElementById('create_goal_form').style.visibility='visible';
    if (type=="music") {
        document.getElementById("create_goal_form").style.width='40%';
        document.getElementById("create_goal_form").style.marginLeft='30%';
    }
}

// Set the date for the calendar input fields in create goal form
document.getElementById('start_date').valueAsDate = new Date();
var tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate()+1);
document.getElementById('end_date').valueAsDate = tomorrow;


goal_tabs = document.getElementsByClassName("goal_links")[0]

function switch_tab(tab){
    current_tab = goal_tabs.getElementsByClassName("active")[0]
    if (current_tab.innerHTML == tab.innerHTML){
        return;
    }
    window.location.href = window.location.href.replace(current_tab.innerHTML+"_goal",tab.innerHTML+"_goal");
}

for (let goal_tab of goal_tabs.children){
    goal_tab.onclick = function() {switch_tab(this)};
}
