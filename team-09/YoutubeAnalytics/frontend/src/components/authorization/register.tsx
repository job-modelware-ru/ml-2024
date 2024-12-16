import React, { useState, useContext, ChangeEvent } from "react";
import "bootstrap/dist/css/bootstrap.css";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import { Context } from "../..";
import { observer } from "mobx-react-lite";

const Register: React.FC = () => {
  const [email, setEmail] = useState<string>("");
  const [name, setName] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const { store } = useContext(Context);

  return (
    <Form>
      <Form.Group>
        <Form.Label>Электронная почта:</Form.Label>
        <Form.Control
          type="text"
          placeholder="Электронная почта"
          value={email}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            setEmail(e.target.value)
          }
        />
      </Form.Group>

      <Form.Group>
        <Form.Label>Логин:</Form.Label>
        <Form.Control
          type="text"
          placeholder="Логин"
          value={name}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            setName(e.target.value)
          }
        />
      </Form.Group>

      <Form.Group>
        <Form.Label>Пароль:</Form.Label>
        <Form.Control
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            setPassword(e.target.value)
          }
        />
      </Form.Group>

      <Button
        variant="primary"
        onClick={() => store.signup(email, name, password)}
      >
        Зарегистрироваться
      </Button>
    </Form>
  );
};

export default observer(Register);
