import {bootstrap} from "./bootstrap.js";
import Api from './api';
import {ReportFinder, ReportConfigurationBuilder} from './reportEngine';
import {getCsrf} from 'util/cookie';
import {DynamicReportApp} from "./view.js";

import React from "react";
import ReactDOM from "react-dom";

bootstrap();

const api = new Api(getCsrf());

const configBuilder = new ReportConfigurationBuilder(api);
const reportFinder = new ReportFinder(api, configBuilder);

ReactDOM.render(
    <DynamicReportApp
        reportFinder={reportFinder}/>,
    document.getElementById("reporting-app")
);
