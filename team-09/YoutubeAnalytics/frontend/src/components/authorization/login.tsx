import React, { useContext, useState } from "react";
import "bootstrap/dist/css/bootstrap.css";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import { Context } from "../..";
import { observer } from "mobx-react-lite";

const Login: React.FC = () => {
  const [emailOrUsername, setEmailOrUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { store } = useContext(Context);

  return (
    <Form>
      <Form.Group>
        <Form.Label>Введите электронную почту или логин:</Form.Label>
        <Form.Control
          type="text"
          placeholder="Введите вашу электронную почту или логин"
          value={emailOrUsername}
          onChange={(e) => setEmailOrUsername(e.target.value)}
        />
      </Form.Group>

      <Form.Group>
        <Form.Label>Введите пароль:</Form.Label>
        <Form.Control
          type="password"
          placeholder="Введите пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </Form.Group>

      {error && <div>{error}</div>}

      <Button
        variant="primary"
        onClick={() => store.login(emailOrUsername, password)}
      >
        Войти
      </Button>
    </Form>
  );
};

export default observer(Login);
