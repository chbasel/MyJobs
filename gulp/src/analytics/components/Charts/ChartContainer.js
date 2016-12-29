import React from 'react';
import {Component} from 'react';
import {Row, Col} from 'react-bootstrap';
import {connect} from 'react-redux';
import SimpleBarChart from './Bar/BarChart';
import WorldMap from './Map/WorldMap';
import USAMap from './Map/USAMap';
import NoResults from 'common/ui/NoResults';
import {isEmpty} from 'lodash-compat/lang';
import {doGetSelectedFilterData} from '../../actions/table-filter-actions';

class ChartContainer extends Component {
  constructor(props, context) {
    super(props, context);
  }
  render() {
    const {chartData, dispatch} = this.props;
    const chartType = chartData.PageLoadData.chart_type;
    // Grab the row data to check and make sure the data coming back isn't empty
    const dataPresent = chartData.PageLoadData.rows;
    const helpError = 'We couldn\'t find any charts using the filters applied.';
    const pathClicked = (tableValue, typeValue) => {
      dispatch(doGetSelectedFilterData(tableValue, typeValue));
    };
    let chartDisplay;
    switch (chartType) {
    case 'map:world':
      chartDisplay = <WorldMap width={1920} height={600} scale={115} chartData={chartData} pathClicked={pathClicked} />;
      break;
    case 'map:nation':
      const country_filter = chartData.activeFilters.filter((x) => x.type === "country")[0] || {};
      if (country_filter.value === 'USA') {
        chartDisplay = <USAMap width={1920} height={600} scale={1100} chartData={chartData} pathClicked={pathClicked} />;
      } else {
        chartDisplay = <SimpleBarChart width={600} height={250} chartData={chartData} pathClicked={pathClicked} />;
      };
      break;
    case 'map:state':
      chartDisplay = <SimpleBarChart width={600} height={250} chartData={chartData} pathClicked={pathClicked} />;
      break;
    case 'string':
      chartDisplay = <SimpleBarChart width={600} height={250} chartData={chartData} pathClicked={pathClicked} />;
      break;
    default:
      chartDisplay = <NoResults type="div" errorMessage="No charts found" helpErrorMessage={helpError} />;
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
              <Col>
                {isEmpty(dataPresent) ? <NoResults type="div" errorMessage="No charts found" helpErrorMessage={helpError}/> : chartDisplay}
              </Col>
            </Row>
        </div>
    );
  }
}

ChartContainer.propTypes = {
  chartData: React.PropTypes.object.isRequired,
  dispatch: React.PropTypes.func.isRequired,
};

export default connect()(ChartContainer);
