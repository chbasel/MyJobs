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
    const chartType = chartData.PageLoadData.column_names[0].key;
    // Grab the row data to check and make sure the data coming back isn't empty
    const dataPresent = chartData.PageLoadData.rows;
    const helpError = 'We couldn\'t find any results using the filters applied. Please change your criteria.';
    let chartDisplay;
    switch (chartType) {
    case 'country':
      chartDisplay = <WorldMap width={1920} height={800} chartData={chartData} />;
      break;
    case 'state':
      chartDisplay = <USAMap width={1920} height={700} chartData={chartData} />;
      break;
    case 'city':
      chartDisplay = <USAMap width={1920} height={700} chartData={chartData} />;
      break;
    case 'found_on':
      chartDisplay = <SimpleBarChart chartData={chartData} />;
      break;
    case 'title':
      chartDisplay = <SimpleBarChart chartData={chartData} />;
      break;
    case 'job_guid':
      chartDisplay = <SimpleBarChart chartData={chartData} />;
      break;
    default:
      chartDisplay = <WorldMap chartData={chartData} />;
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
                {isEmpty(dataPresent) ? <NoResults type="div" errorMessage="No results found" helpErrorMessage={helpError}/> : chartDisplay}
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
