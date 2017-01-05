import React from 'react';
import {Component} from 'react';
import {Row, Col} from 'react-bootstrap';
import SimpleBarChart from './Bar/BarChart';
import WorldMap from './Map/WorldMap';
import USAMap from './Map/USAMap';
import NoResults from 'common/ui/NoResults';
import {isEmpty} from 'lodash-compat/lang';

class ChartContainer extends Component {
  constructor(props, context) {
    super(props, context);

    this.state = {
      width: 0,
    };
  }
  componentDidMount() {
    this.handleChartWidth();
  }
  handleChartWidth() {
    this.setState({
      width: this.refs.chartContainer.clientWidth,
    });
  }
  render() {
    const {chartData} = this.props;
    const chartType = chartData.PageLoadData.chart_type;
    // Grab the row data to check and make sure the data coming back isn't empty
    const dataPresent = chartData.PageLoadData.rows;
    const chartTitleByDisplay = chartData.PageLoadData.column_names[0].label;
    const chartTitleDisplay = chartData.PageLoadData.column_names[1].label;
    const title = `${chartTitleDisplay} by ${chartTitleByDisplay}`;
    const ranges = ['rgb(254,229,217)', 'rgb(252,187,161)', 'rgb(252,146,114)', 'rgb(251,106,74)', 'rgb(239,59,44)', 'rgb(203,24,29)', 'rgb(153,0,13)'];
    const helpError = 'We couldn\'t find any charts using the filters applied.';
    let chartDisplay;
    switch (chartType) {
    case 'map:world':
      chartDisplay = <WorldMap width={this.state.width} height={500} projectionScale={95} chartData={chartData} colorRange={ranges} />;
      break;
    case 'map:nation':
      chartDisplay = <USAMap width={this.state.width} height={500} scale={950} chartData={chartData} colorRange={ranges} />;
      break;
    case 'map:state':
      chartDisplay = <SimpleBarChart width={600} height={400} chartData={chartData} />;
      break;
    case 'string':
      chartDisplay = <SimpleBarChart width={600} height={400} chartData={chartData} />;
      break;
    default:
      chartDisplay = <NoResults type="div" errorMessage="No charts found" helpErrorMessage={helpError}/>;
    }
    return (
        <div id={'chart_tab_' + chartData.navId} className="charts" ref="chartContainer">
          <Row>
            <Col md={12}>
              <div className="chart-title">
                <h2>{title}</h2>
              </div>
            </Col>
          </Row>
          <hr/>
            <Row>
              <Col md={12}>
                {isEmpty(dataPresent) ? <NoResults type="div" errorMessage="No charts found" helpErrorMessage={helpError}/> : chartDisplay}
              </Col>
            </Row>
        </div>
    );
  }
}

ChartContainer.propTypes = {
  chartData: React.PropTypes.object.isRequired,
};

export default ChartContainer;
