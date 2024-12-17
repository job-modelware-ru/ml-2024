import Tab from "react-bootstrap/Tab";
import Tabs from "react-bootstrap/Tabs";
import Register from "./register";
import Login from "./login";

import "bootstrap/dist/css/bootstrap.css";
import { observer } from "mobx-react-lite";

const Authorization = () => {
  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-lg-6">
          <Tabs defaultActiveKey="login" className="mt-5">
            <Tab eventKey="login" title="Войти" className="w-50">
              <Login />
            </Tab>
            <Tab eventKey="signup" title="Регистрация">
              <Register />
            </Tab>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default observer(Authorization);
