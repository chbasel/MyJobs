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
  }
  render() {
    const {chartData} = this.props;
    const chartType = chartData.PageLoadData.chart_type;
    // Grab the row data to check and make sure the data coming back isn't empty
    const dataPresent = chartData.PageLoadData.rows;
    const helpError = 'We couldn\'t find any charts using the filters applied.';
    let chartDisplay;
    switch (chartType) {
    case 'map:world':
      chartDisplay = <WorldMap width={1920} height={500} scale={105} chartData={chartData} />;
      break;
    case 'map:nation':
      chartDisplay = <USAMap width={1920} height={500} scale={1100} chartData={chartData} />;
      break;
    case 'map:state':
      chartDisplay = <USAMap width={1920} height={500} scale={1100} chartData={chartData} />;
      break;
    case 'string':
      chartDisplay = <SimpleBarChart width={600} height={400} chartData={chartData} />;
      break;
    default:
      chartDisplay = <NoResults type="div" errorMessage="No charts found" helpErrorMessage={helpError}/>;
    }
    return (
        <div id={'chart_tab_' + chartData.navId} className="charts">
          <Row>
            <Col md={12}>
              <div className="chart-title">
                <h2>Job Locations</h2>
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
