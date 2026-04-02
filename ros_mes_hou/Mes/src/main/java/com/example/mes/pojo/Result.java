package com.example.mes.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Result<T> {
    private int code;       // 状态码 (如 200 成功，400 失败)
    private String msg;    // 提示信息
    private T data;        // 返回数据

    public static <T> Result<T> success() {
        return new Result<>(200,"success",null);
    }
    // 成功静态方法
    public static <T> Result<T> success(T data) {
        return new Result<>(200, "success", data);
    }

    // 失败静态方法
    public static <T> Result<T> error(int code, String msg) {
        return new Result<>(code, msg, null);
    }
}