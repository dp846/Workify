document.getElementsByClassName("active")[0].classList.remove("active");
document.getElementById("progress_link").classList.add("active");

var progress_tabs = document.getElementsByClassName("progress_links")[0];
var myChart = new Chart("chart");

function switch_tab(tab){
    current_tab = progress_tabs.getElementsByClassName("active")[0];
    if (current_tab.innerHTML == tab.innerHTML){
        return;
    }
    current_tab.classList.remove("active");
    tab.classList.add("active");
}

function productivity(tab) {
    switch_tab(tab);
    myChart.destroy();

    Chart.defaults.global.defaultFontColor = "#0e2d3c";

    var bar_ctx = document.getElementById('chart').getContext('2d');

    var background_1 = bar_ctx.createLinearGradient(0, 0, 0, 600);
    background_1.addColorStop(0, 'yellow');
    background_1.addColorStop(1, 'red');
    myChart = new Chart("chart",
    {
        type: "bar",
        data:
        {
            labels: xValues,
            datasets:
            [{
                label: "Hours spent working",
                backgroundColor: background_1,
                data: yValues
            }]
        },
        options:
        {
            legend: {
                display: false
            },
            scales:
            {
                xAxes:
                [{
                gridLines:
                    {
                        color: background_1
                    },
                    display: true,
                    position: 'bottom',
                    scaleLabel: {
                        display: true,
                        labelString: 'Dates',
                        fontSize: 12,
                        fontColor: '#0e2d3c',
                    },
                }],
                yAxes:
                [{
                gridLines:
                    {
                        color: background_1
                    },
                    display: true,
                    position: 'left',
                    scaleLabel: {
                        display: true,
                        labelString: 'Hours Spent Working',
                        fontSize: 12,
                        fontColor: '#0e2d3c',
                    },
                    ticks:{
                        beginAtZero: true
                    }
                }]
            }
        }
    });
};

function track_properties(tab) {
    switch_tab(tab);
    myChart.destroy();

    Chart.defaults.global.defaultFontColor = "#0e2d3c";

    var chr_ctx = document.getElementById('chart').getContext('2d');

    var background_1 = chr_ctx.createLinearGradient(0, 0, 0, 800);
    var background_2 = chr_ctx.createLinearGradient(0, 0, 0, 800);

    background_1.addColorStop(0, 'rgba(255,255,0,0.85)');
    background_1.addColorStop(1, 'rgba(255,0,0,0.85)');

    background_2.addColorStop(0, 'rgba(0,255,0,0.85)');
    background_2.addColorStop(1, 'rgba(0,0,150,0.85)');

    new Chart("chart",
    {
        type: 'radar',
        data:
        {
            labels: labels,
            datasets:
            [{
                label: "Recent track properties (click this text to hide)",
                backgroundColor: background_1,
                borderColor: 'orange',
                data: data
            },
            {
                label: "Properties on most productive day (click this text to hide)",
                backgroundColor: background_2,
                borderColor: 'green',
                data: data2
            }]
        },
        options:
        {
            legend: {
                display: true
            },
            title:
            {
                display: true
            },
            scale:
            {
                ticks:
                {
                    beginAtZero: true,
                    max: 1,
                    min: 0,
                    stepSize: 0.1,
                    display: false
                }
            }
        }
    });
}

productivity(progress_tabs.getElementsByClassName("active")[0]);