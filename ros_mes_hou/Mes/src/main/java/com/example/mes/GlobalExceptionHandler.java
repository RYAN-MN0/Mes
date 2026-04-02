package com.example.mes;

import com.example.mes.pojo.Result;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;

import java.sql.SQLIntegrityConstraintViolationException;

@ControllerAdvice
public class GlobalExceptionHandler {

    /**
     * 处理 MySQL 唯一键冲突异常 (Duplicate Entry)
     */
    @ExceptionHandler(DuplicateKeyException.class)
    @ResponseBody
    public Result handleDuplicateKeyException(DuplicateKeyException e) {
        // 1. 获取底层真实的异常信息
        Throwable rootCause = e.getRootCause();

        if (rootCause instanceof SQLIntegrityConstraintViolationException) {
            SQLIntegrityConstraintViolationException sqlEx = (SQLIntegrityConstraintViolationException) rootCause;

            // 2. 提取报错信息 (示例信息：Duplicate entry '1001' for key 'user.tbl_user_id_unique')
            String errorMsg = sqlEx.getMessage();

            // 3. 解析错误信息，提取关键内容（例如提取出重复的 ID）
            String customMsg = "数据重复：";
            if (errorMsg.contains("Duplicate entry")) {
                // 简单解析：提取重复的键值部分
                String[] parts = errorMsg.split("'");
                if (parts.length >= 2) {
                    customMsg += "【" + parts[1] + "】已存在，请更换";
                } else {
                    customMsg += "违反唯一约束";
                }
            }

            // 4. 返回给前端
            return Result.error(400, customMsg);
        }

        // 兜底处理
        return Result.error(500, "数据库约束冲突");
    }

}