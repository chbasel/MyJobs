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
    const {chartData, dispatch, width} = this.props;
    const chartType = chartData.PageLoadData.chart_type;
    const worldHeight = (width * 0.4);
    const usaHeight = (width * 0.341);
    const usaWidth = (width / 1.45);
    const worldWidth = (width / 1.3);
    const worldScale = (width * 0.083);
    // Grab the row data to check and make sure the data coming back isn't empty
    const dataPresent = chartData.PageLoadData.rows;
    const chartTitleByDisplay = chartData.PageLoadData.column_names[0].label;
    const chartTitleDisplay = chartData.PageLoadData.column_names[1].label;
    const title = `${chartTitleDisplay} by ${chartTitleByDisplay}`;
    const ranges = ['rgb(254,229,217)', 'rgb(252,187,161)', 'rgb(252,146,114)', 'rgb(251,106,74)', 'rgb(239,59,44)', 'rgb(203,24,29)', 'rgb(153,0,13)'];
    const helpError = 'We couldn\'t find any charts using the filters applied.';
    const pathClicked = (tableValue, typeValue) => {
      dispatch(doGetSelectedFilterData(tableValue, typeValue));
    };
    let chartDisplay;
    switch (chartType) {
    case 'map:world':
      chartDisplay = <WorldMap width={worldWidth} height={worldHeight} projectionScale={worldScale} chartData={chartData} colorRange={ranges} pathClicked={pathClicked}/>;
      break;
    case 'map:nation':
      const countryFilter = chartData.activeFilters.filter((x) => x.type === 'country')[0] || {};
      if (countryFilter.value === 'USA') {
        chartDisplay = <USAMap width={usaWidth} height={usaHeight} chartData={chartData} colorRange={ranges} pathClicked={pathClicked}/>;
      } else {
        chartDisplay = <SimpleBarChart width={600} height={400} chartData={chartData} pathClicked={pathClicked} />;
      }
      break;
    case 'map:state':
      chartDisplay = <SimpleBarChart width={600} height={400} chartData={chartData} pathClicked={pathClicked} />;
      break;
    case 'string':
      chartDisplay = <SimpleBarChart width={600} height={400} chartData={chartData} pathClicked={pathClicked} />;
      break;
    default:
      chartDisplay = <NoResults type="div" errorMessage="No charts found" helpErrorMessage={helpError} />;
    }
    return (
        <div id={'chart_tab_' + chartData.navId} className="charts">
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
                <div className="svg-container">
                  {isEmpty(dataPresent) ? <NoResults type="div" errorMessage="No charts found" helpErrorMessage={helpError}/> : chartDisplay}
                </div>
              </Col>
            </Row>
        </div>
    );
  }
}

ChartContainer.propTypes = {
  chartData: React.PropTypes.object.isRequired,
  width: React.PropTypes.number.isRequired,
  dispatch: React.PropTypes.func.isRequired,
};

export default connect()(ChartContainer);
