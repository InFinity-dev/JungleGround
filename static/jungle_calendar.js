//날짜를 클릭하면 일정을 하단에 보여주게 하는 함수
function showTask(month, date){ //누가(팀원 or 조장) 클릭하느냐에 따라 일정을 다르게 가져와야 하니, 변수하나 더 받아오긴해야 함...
    $.ajax({
        type: "POST",
        url: "/test", //어떤 url로 접근할지? 날짜 별로 서버에 매번 접근?
        data: {'month_give': month, 'date_give': date},
        success: function(response) {
            if(response["result"] == "success"){
                alert(response['task']);
                document.getElementById('todayTask').innerHTML = '';
                for (var i = 0; i<response['task'].length; i++){
                    let tempHtml = `<li>${response['task'][i]}</li>`;
                    $("#todayTask").append(tempHtml);
                }
        }
    }})
}

// 달력 표시하는 함수
function jungle_calendar(id, today) {
	
if( typeof(today) != 'undefined' ) {
      today = today.split('-');
      today[1] = today[1] - 1;
      today = new Date(today[0], today[1], today[2]);
   } else {
	   var today = new Date();
   }
var year = today.getFullYear();
var month = today.getMonth() + 1;
var date = today.getDate();
today.setDate(1);
var day = today.getDay();
var d = new Date();

var lastDate = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

if(year % 4 == 0 && year % 100 != 0 || year % 400 == 0)
    lastDate[1] = 29;
	
var nowLastDate = lastDate[month - 1]; //이번달의 요일 수

var week = Math.ceil((day+nowLastDate)/7); 

//var prevMonthToday = new Date(year, month-1, date);
//var nextMonthToday = new Date(year, month+1, date);
	
var prevMonthToday = year + '-' + (month - 1) + '-' + date;
var nextMonthToday = year + '-' + (month + 1) + '-' + date;
var prevYearToday = (year - 1) + '-' + month + '-' + date;
var nextYearToday = (year + 1) + '-' + month + '-' + date;

var calendar = "<div class='calendar_div'>";
calendar += "<p>";
calendar += "<a href='#' class='button' onclick= 'jungle_calendar(\""+id+"\", \""+prevYearToday+"\")'><img src='/static/btn_year_prev.gif'/></a>";
calendar += "<a href='#' class='button' onclick= 'jungle_calendar(\""+id+"\", \""+prevMonthToday+"\")'><img src='/static/btn_month_prev.gif'/></a>";
calendar += year + '년' + month + '월';
calendar += "<a href=#' class='button' onclick= 'jungle_calendar(\""+id+"\", \""+nextMonthToday+"\")'><img src='/static/btn_month_next.gif'/></a>";
calendar += "<a href='#' class='button' onclick= 'jungle_calendar(\""+id+"\", \""+nextYearToday+"\")'><img src='/static/btn_year_next.gif'/></a>";
calendar += "</p>";
calendar += "<table class='calendar_table'>";
calendar += "<tr>";
calendar += "<th class='sun'>일</th>";
calendar += "<th>월</th>";
calendar += "<th>화</th>";
calendar += "<th>수</th>";
calendar += "<th>목</th>";
calendar += "<th>금</th>";
calendar += "<th class='sat'>토</th>";
calendar += "</tr>";

var countDate = 1;
var count = 0;
var prevCountDate = lastDate[month-2] - (day - 1);
if(month == 1) {
	prevCountDate = lastDate[11] - (day - 1);
}
var nextCountDate = 1;

for(var i = 1; i <= week; i++) {
    calendar += "<tr>";
    for(var j = 1; j <= 7; j++) {
        if(year == d.getFullYear() && month == d.getMonth() + 1 && countDate == d.getDate()) {
            calendar += `<td class="button" style='cursor: pointer; background-color: #cccccc' id = "${month}" headers = "${countDate}" onclick = "showTask(${month}, ${countDate})">` + countDate + "</td>";
            countDate++;
        } else if(i == 1 && j <= day) {
            prevMonth = month-1 //지역변수
            calendar += `<td style='cursor: pointer;' class='prev' id = "${prevMonth}" headers = "${prevCountDate}" onclick= "showTask(${prevMonth}, ${prevCountDate})">` + prevCountDate + "</td>";
            prevCountDate++;
        } else if(countDate > nowLastDate) {
            nextMonth = month+1 //지역변수
            calendar += `<td style='cursor: pointer;' class='next' id = "${nextMonth}" headers = "${nextCountDate}" onclick = "showTask(${nextMonth}, ${nextCountDate})">` + nextCountDate + "</td>";
            nextCountDate++;
        } else if(count == 0) {
            calendar += `<td style='cursor: pointer;' class='sun' id = "${month}" headers = "${countDate}" onclick = "showTask(${month}, ${countDate})">` + countDate + "</td>";
            countDate++;
        } else if(count == 6) {
            calendar += `<td style='cursor: pointer;' class='sat' id = "${month}" headers = "${countDate}" onclick = "showTask(${month}, ${countDate})">` + countDate + "</td>";
            countDate++;
        } else {
            calendar += `<td style='cursor: pointer;' id = "${month}" headers = "${countDate}" onclick = "showTask(${month}, ${countDate})">` + countDate + "</td>";
            countDate++;
        }
        count++;
        if(count == 7) {
            count = 0;
        }
    }
    calendar += "</tr>";
}
document.getElementById("junglecalendar").innerHTML = calendar;
}

window.onload=function(){
    jungle_calendar();
}