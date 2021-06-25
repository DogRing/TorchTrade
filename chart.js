Highcharts.chart('chartDisplay', {
    chart: {
        type: 'spline'
    },
    title: {
        text: 'Live Data (CSV)'
    },

    subtitle: {
        text: 'Data input from a remote CSV file'
    },

    data: {
        csv: document.getElementById('data').innerHTML,
        enablePolling: true
    }
});
